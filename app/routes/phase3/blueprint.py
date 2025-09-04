# app/routes/phase3/blueprint.py
"""
Flask blueprint for Phase 3 CV processing endpoints
Optimized and organized structure
"""
import os
import tempfile
import zipfile
from pathlib import Path
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from datetime import datetime

from .config import (
    ALLOWED_TEMPLATE_EXTENSIONS, 
    ALLOWED_CV_EXTENSIONS,
    get_upload_folder,
    get_output_folder,
    allowed_file,
    create_directories
)
from .session_manager import (
    create_session,
    get_session,
    processing_sessions
)
from .processor import start_processing_thread

# Try to import CV processor for testing
try:
    import sys
    project_root = Path(__file__).parent.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    from app.cv_processor.utils.ai_client import get_ai_client
    CV_PROCESSOR_AVAILABLE = True
    print("✓ CV Processor modules loaded successfully")
except ImportError as e:
    print(f"⚠ CV Processor not available: {e}")
    CV_PROCESSOR_AVAILABLE = False

phase3_bp = Blueprint('phase3', __name__, url_prefix='/phase3')

@phase3_bp.route('/process', methods=['POST'])
def process_cvs():
    """Process uploaded template and CV files asynchronously"""
    try:
        create_directories()
        
        # Validate files
        if 'template' not in request.files or 'cv_files' not in request.files:
            return jsonify({'error': 'Missing template or CV files'}), 400
        
        template_file = request.files['template']
        cv_files = request.files.getlist('cv_files')
        
        # Validate template file
        if template_file.filename == '' or not allowed_file(template_file.filename, ALLOWED_TEMPLATE_EXTENSIONS):
            return jsonify({'error': 'Invalid template file. Please upload a .docx file.'}), 400
        
        # Validate CV files
        if not cv_files or len(cv_files) == 0:
            return jsonify({'error': 'No CV files uploaded'}), 400
        
        for cv_file in cv_files:
            if cv_file.filename == '' or not allowed_file(cv_file.filename, ALLOWED_CV_EXTENSIONS):
                return jsonify({'error': f'Invalid CV file: {cv_file.filename}. Please upload .pdf or .docx files.'}), 400
        
        # Create session and save files
        session_id = create_session(len(cv_files))
        session_folder = get_upload_folder() / session_id
        session_folder.mkdir(exist_ok=True)
        
        # Save template file
        template_filename = secure_filename(template_file.filename)
        template_path = session_folder / template_filename
        template_file.save(str(template_path))
        
        # Save CV files
        cv_paths = []
        for cv_file in cv_files:
            cv_filename = secure_filename(cv_file.filename)
            cv_path = session_folder / cv_filename
            cv_file.save(str(cv_path))
            cv_paths.append(cv_path)
        
        # Start processing in background
        start_processing_thread(template_path, cv_paths, session_id)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'status': 'processing',
            'message': 'Processing started. Use /status endpoint to track progress.'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error starting CV processing: {str(e)}")
        return jsonify({'error': 'An error occurred while starting processing'}), 500

@phase3_bp.route('/test-ai')
def test_ai():
    """Test endpoint to verify AI integration"""
    try:
        if not CV_PROCESSOR_AVAILABLE:
            return jsonify({
                'error': 'CV Processor not available',
                'cv_processor_available': False
            }), 500
        
        # Test AI client
        client = get_ai_client()
        
        # Simple test prompt
        test_response = client.generate([
            {"role": "user", "content": "Return a simple JSON object with a 'test' key and 'success' value."}
        ])
        
        result = client.extract_json_from_response(test_response)
        
        return jsonify({
            'ai_test': 'success',
            'cv_processor_available': True,
            'response': result
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'ai_test': 'failed',
            'cv_processor_available': CV_PROCESSOR_AVAILABLE
        }), 500

@phase3_bp.route('/status/<session_id>')
def get_status(session_id):
    """Get real-time processing status for a session"""
    try:
        # Check if session exists in memory
        if session_id in processing_sessions:
            session = get_session(session_id)
            return jsonify({
                'status': session['status'],
                'progress': session['progress'],
                'current_step': session['current_step'],
                'total_files': session['total_files'],
                'processed_files': session['processed_files'],
                'files': session.get('files', []),
                'total_processed': session.get('total_processed', 0),
                'error': session.get('error')
            })
        
        # Fallback: check if files exist on disk (for completed sessions)
        session_folder = get_output_folder() / session_id
        if session_folder.exists():
            files = list(session_folder.glob('*.docx'))
            return jsonify({
                'status': 'completed',
                'progress': 100,
                'current_step': 'Complete!',
                'files_count': len(files),
                'files': [{'name': f.name, 'id': f"{session_id}/{f.name}"} for f in files],
                'total_processed': len(files)
            })
        
        return jsonify({'status': 'not_found'}), 404
        
    except Exception as e:
        current_app.logger.error(f"Error getting status: {str(e)}")
        return jsonify({'error': 'Status check failed'}), 500

@phase3_bp.route('/download/<path:file_id>')
def download_file(file_id):
    """Download a processed file"""
    try:
        # Parse session_id and filename from file_id
        parts = file_id.split('/', 1)
        if len(parts) != 2:
            return jsonify({'error': 'Invalid file ID'}), 400
        
        session_id, filename = parts
        file_path = get_output_folder() / session_id / filename
        
        if not file_path.exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        current_app.logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@phase3_bp.route('/download-all/<session_id>')
def download_all_files(session_id):
    """Download all processed files as a ZIP archive"""
    try:
        session_folder = get_output_folder() / session_id
        if not session_folder.exists():
            return jsonify({'error': 'Session not found'}), 404
        
        files = list(session_folder.glob('*.docx'))
        if not files:
            return jsonify({'error': 'No files found'}), 404
        
        # Create a temporary ZIP file
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            temp_zip_path = temp_zip.name
        
        try:
            with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in files:
                    zip_file.write(file_path, file_path.name)
            
            # Generate a meaningful filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"processed_cvs_{timestamp}.zip"
            
            return send_file(
                temp_zip_path,
                as_attachment=True,
                download_name=zip_filename,
                mimetype='application/zip'
            )
        except Exception as zip_error:
            try:
                os.unlink(temp_zip_path)
            except:
                pass
            raise zip_error
        
    except Exception as e:
        current_app.logger.error(f"Error creating ZIP download: {str(e)}")
        return jsonify({'error': 'ZIP creation failed'}), 500
