# app/routes/phase3/session_manager.py
"""
Session management for Phase 3 CV processing
"""
import uuid
from typing import Dict, Any

# Global dictionary to track processing sessions
processing_sessions: Dict[str, Dict[str, Any]] = {}

def create_session(total_files: int) -> str:
    """Create a new processing session"""
    session_id = str(uuid.uuid4())
    processing_sessions[session_id] = {
        'status': 'starting',
        'progress': 0,
        'current_step': 'Initializing...',
        'total_files': total_files,
        'processed_files': 0,
        'files': [],
        'error': None
    }
    return session_id

def update_session(session_id: str, **kwargs) -> None:
    """Update session data"""
    if session_id in processing_sessions:
        processing_sessions[session_id].update(kwargs)

def get_session(session_id: str) -> Dict[str, Any]:
    """Get session data"""
    return processing_sessions.get(session_id, {})

def complete_session(session_id: str, output_files: list) -> None:
    """Mark session as completed"""
    if session_id in processing_sessions:
        processing_sessions[session_id].update({
            'status': 'completed',
            'progress': 100,
            'current_step': 'Complete!',
            'processed_files': len(output_files),
            'files': output_files,
            'total_processed': len(output_files)
        })

def error_session(session_id: str, error: str) -> None:
    """Mark session as failed"""
    if session_id in processing_sessions:
        processing_sessions[session_id].update({
            'status': 'error',
            'error': error,
            'current_step': f'Error: {error}'
        })
