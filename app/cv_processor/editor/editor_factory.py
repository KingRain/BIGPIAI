# cv_processor/editor/editor_factory.py
"""
DOCX editor factory and utilities with validation pipeline.
"""
from typing import Dict, Any, List
import os
from pathlib import Path

try:
    from app.cv_processor.editor.docxedit_editor import DocxEditEditor, DOCXEDIT_AVAILABLE
except ImportError:
    DocxEditEditor = None
    DOCXEDIT_AVAILABLE = False

try:
    from app.cv_processor.editor.python_docx_editor import PythonDocxEditor, PYTHON_DOCX_AVAILABLE
except ImportError:
    PythonDocxEditor = None
    PYTHON_DOCX_AVAILABLE = False


def create_docx_editor(file_path: str):
    """Create the appropriate DOCX editor based on available packages."""
    if DOCXEDIT_AVAILABLE:
        return DocxEditEditor(file_path)
    elif PYTHON_DOCX_AVAILABLE:
        return PythonDocxEditor(file_path)
    else:
        raise RuntimeError("Neither docxedit nor python-docx packages are available. Install one of them.")


def apply_positional_replacements(
    template_path: str,
    output_path: str,
    execution_plan: List[Dict[str, Any]],
    position_map: Dict[str, Any]
) -> None:
    """Apply positional replacements to a DOCX file."""
    editor = create_docx_editor(template_path)

    print(f"[DocxEdit] Applying {len(execution_plan)} precise replacements using {editor.editor_type}...")

    replacements_made = 0
    for item in execution_plan:
        location_id = item.get("location_id")
        placeholder_text = item.get("placeholder_text", "")
        value = item.get("value_to_insert")

        if not location_id or location_id not in position_map:
            print(f"[Warning] Location ID '{location_id}' not found in position map")
            continue

        if value is None or str(value).strip().upper() == "N/A":
            continue

        replacement_value = str(value).strip()

        if editor.replace_at_position(location_id, placeholder_text, replacement_value, position_map):
            replacements_made += 1
            print(f"[DocxEdit] Replaced at {location_id}: '{placeholder_text}' -> '{replacement_value[:50]}...'")

    editor.save(output_path)
    print(f"[DocxEdit] Document saved: {output_path} ({replacements_made} replacements made)")
