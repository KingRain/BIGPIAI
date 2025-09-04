# cv_processor/editor/base_editor.py
"""
Base DOCX editor with common functionality.
"""
import os
from typing import Dict, Any, List


class BaseDocxEditor:
    """Base class for DOCX editors with common functionality."""

    def __init__(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")
        self.file_path = file_path
        self.doc = None
        self.editor_type = "base"

    def get_enumerated_structure(self) -> tuple[str, Dict[str, Any]]:
        """Extract document content with unique positional identifiers."""
        raise NotImplementedError("Subclasses must implement get_enumerated_structure")

    def replace_at_position(self, location_id: str, placeholder: str, replacement: str, position_map: Dict[str, Any]) -> bool:
        """Replace text at specific document position."""
        raise NotImplementedError("Subclasses must implement replace_at_position")

    def save(self, output_path: str = None) -> None:
        """Save the document."""
        raise NotImplementedError("Subclasses must implement save")

    def get_text(self) -> str:
        """Get all text from the document."""
        raise NotImplementedError("Subclasses must implement get_text")

    def _is_heading_or_label(self, paragraph) -> bool:
        """Check if paragraph is likely a heading or label that shouldn't be replaced."""
        # Check if paragraph has heading style
        if hasattr(paragraph, 'style') and paragraph.style and 'heading' in paragraph.style.name.lower():
            return True

        # Check if text is all bold (likely a label/heading)
        if paragraph.runs:
            bold_chars = sum(len(run.text) for run in paragraph.runs if run.bold)
            total_chars = len(paragraph.text)
            if total_chars > 0 and bold_chars / total_chars > 0.7:  # 70% or more bold
                return True

        # Check for label patterns (ends with colon)
        text = paragraph.text.strip()
        if text.endswith(':') and len(text.split()) <= 3:  # Short text ending with colon
            return True

        return False

    def _replace_in_runs(self, runs, placeholder: str, replacement: str) -> bool:
        """Replace text in runs while preserving formatting."""
        replaced = False

        for run in runs:
            if placeholder in run.text:
                # Store original formatting
                original_bold = run.bold
                original_italic = run.italic
                original_underline = run.underline
                original_font_name = run.font.name if run.font else None
                original_font_size = run.font.size if run.font else None

                # Replace text
                run.text = run.text.replace(placeholder, replacement)

                # Restore formatting
                run.bold = original_bold
                run.italic = original_italic
                run.underline = original_underline
                if original_font_name and run.font:
                    run.font.name = original_font_name
                if original_font_size and run.font:
                    run.font.size = original_font_size

                replaced = True

        return replaced
