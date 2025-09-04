# app/routes/phase3/config.py
"""
Configuration settings for Phase 3 CV processing
"""
from pathlib import Path
from flask import current_app

# File extensions
ALLOWED_TEMPLATE_EXTENSIONS = {'docx'}
ALLOWED_CV_EXTENSIONS = {'pdf', 'docx'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def get_upload_folder():
    """Get upload folder path"""
    try:
        return Path(current_app.instance_path) / 'uploads' / 'phase3'
    except RuntimeError:
        return Path('uploads/phase3')

def get_output_folder():
    """Get output folder path"""
    project_root = Path(__file__).parent.parent.parent.parent
    return project_root / 'outputs' / 'phase3'

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def create_directories():
    """Create necessary directories if they don't exist"""
    get_upload_folder().mkdir(parents=True, exist_ok=True)
    get_output_folder().mkdir(parents=True, exist_ok=True)
