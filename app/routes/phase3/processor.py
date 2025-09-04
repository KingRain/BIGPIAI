# app/routes/phase3/processor.py
"""
Main processing logic for Phase 3 CV processing
Implements the simplified pipeline with optimized Gemini AI calls
"""
import threading
import time
from pathlib import Path
from flask import current_app

from .cv_processor import (
    extract_template_placeholders,
    extract_cv_texts,
    map_cv_to_template,
    generate_document
)
from .session_manager import update_session, complete_session, error_session
from .config import get_output_folder

def process_cv_files_async(template_path: Path, cv_paths: list, session_id: str) -> None:
    """
    Asynchronous CV processing using simplified pipeline
    Based on cv_processor simple_main.py approach with 1 API call per CV
    """
    try:
        print(f"[DEBUG] Starting simplified pipeline for session {session_id}")
        
        # Step 1: Extract Jinja placeholders from template (No AI call)
        update_session(session_id, 
                      status='processing',
                      current_step='Analyzing template...',
                      progress=10)
        
        template_text, jinja_placeholders = extract_template_placeholders(template_path)
        
        if not jinja_placeholders:
            raise ValueError("No Jinja placeholders found in template")
        
        # Step 2: Extract text from CV files (No AI call)
        update_session(session_id,
                      current_step='Extracting CV content...',
                      progress=20)
        
        cv_list = extract_cv_texts(cv_paths)
        
        if not cv_list:
            raise ValueError("No readable content found in CV files")
        
        print(f"[DEBUG] Extracted text from {len(cv_list)} CV files")
        
        # Step 3: Process each CV with AI mapping (1 API call per CV)
        update_session(session_id,
                      current_step='Processing CVs with AI...',
                      progress=30)
        
        output_files = []
        output_session_folder = get_output_folder() / session_id
        output_session_folder.mkdir(exist_ok=True)
        
        total_cvs = len(cv_list)
        for i, (filepath, resume_text) in enumerate(cv_list):
            try:
                # Update progress for current CV
                cv_progress = 30 + (i / total_cvs) * 60  # 30% to 90%
                update_session(session_id,
                              progress=int(cv_progress),
                              current_step=f'Processing CV {i+1} of {total_cvs}: {Path(filepath).name}',
                              processed_files=i)
                
                print(f"[DEBUG] Processing CV {i+1}/{total_cvs}: {Path(filepath).name}")
                print(f"[DEBUG] Resume text length: {len(resume_text)} characters")
                
                # Map placeholders to values using AI (1 API call per CV)
                placeholder_to_value = map_cv_to_template(
                    jinja_placeholders, resume_text, template_text
                )
                
                # Generate output filename with 'finished' prefix
                base_name = Path(filepath).stem
                if base_name.startswith("01_"):
                    output_base = "02_finished_" + base_name[3:]
                else:
                    output_base = "02_finished_" + base_name
                output_path = output_session_folder / f"{output_base}.docx"
                
                # Generate document using DocxTemplate
                generate_document(template_path, placeholder_to_value, output_path)
                
                output_files.append({
                    'id': f"{session_id}/{output_path.name}",
                    'name': output_path.name,
                    'original_cv': Path(filepath).name
                })
                
                # Small delay to show progress
                time.sleep(0.1)
                
            except Exception as e:
                print(f"[ERROR] Error processing {Path(filepath).name}: {str(e)}")
                current_app.logger.error(f"Error processing {Path(filepath).name}: {str(e)}")
                continue
        
        if not output_files:
            raise ValueError("No files were successfully processed")
        
        # Complete processing
        complete_session(session_id, output_files)
        print(f"[DEBUG] Processing completed. Generated {len(output_files)} files.")
        
    except Exception as e:
        print(f"[ERROR] Processing failed for session {session_id}: {str(e)}")
        error_session(session_id, str(e))
        current_app.logger.error(f"Processing failed for session {session_id}: {str(e)}")

def start_processing_thread(template_path: Path, cv_paths: list, session_id: str) -> None:
    """Start processing in background thread"""
    thread = threading.Thread(
        target=process_cv_files_async,
        args=(template_path, cv_paths, session_id)
    )
    thread.daemon = True
    thread.start()
