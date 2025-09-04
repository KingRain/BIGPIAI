# cv_processor/editor/docxedit_editor.py
"""
DocxEdit package based editor implementation.
"""
from typing import Dict, Any, Tuple

try:
    from docxedit import Document
    DOCXEDIT_AVAILABLE = True
except ImportError:
    Document = None
    DOCXEDIT_AVAILABLE = False

from app.cv_processor.editor.base_editor import BaseDocxEditor


class DocxEditEditor(BaseDocxEditor):
    """DOCX editor using docxedit package."""

    def __init__(self, file_path: str):
        super().__init__(file_path)
        if not DOCXEDIT_AVAILABLE:
            raise RuntimeError("docxedit package is not available.")
        self.doc = Document(file_path)
        self.editor_type = "docxedit"

    def get_enumerated_structure(self) -> Tuple[str, Dict[str, Any]]:
        """Extract document content with unique positional identifiers using docxedit."""
        enumerated_lines = []
        position_map = {}

        # Use docxedit methods
        paragraphs = self.doc.paragraphs
        tables = self.doc.tables

        # Process paragraphs
        for i, paragraph in enumerate(paragraphs):
            para_id = f"PARAGRAPH_{i}"
            text = paragraph.text.strip() if hasattr(paragraph, 'text') else str(paragraph).strip()
            if text:
                enumerated_lines.append(f"{para_id}::{text}")
                position_map[para_id] = {
                    "type": "paragraph",
                    "index": i,
                    "text": text
                }

        # Process tables
        for t_idx, table in enumerate(tables):
            table_id = f"TABLE_{t_idx}"
            if hasattr(table, 'rows'):
                for r_idx, row in enumerate(table.rows):
                    if hasattr(row, 'cells'):
                        for c_idx, cell in enumerate(row.cells):
                            cell_text = cell.text.strip() if hasattr(cell, 'text') else str(cell).strip()
                            if cell_text:
                                cell_id = f"{table_id}_ROW_{r_idx}_COL_{c_idx}"
                                enumerated_lines.append(f"{cell_id}::{cell_text}")
                                position_map[cell_id] = {
                                    "type": "table_cell",
                                    "table_index": t_idx,
                                    "row": r_idx,
                                    "col": c_idx,
                                    "text": cell_text
                                }

        enumerated_text = "\n".join(enumerated_lines)
        return enumerated_text, position_map

    def replace_at_position(self, location_id: str, placeholder: str, replacement: str, position_map: Dict[str, Any]) -> bool:
        """Replace text at specific document position using docxedit."""
        if location_id not in position_map:
            return False

        position_info = position_map[location_id]
        element_type = position_info["type"]

        try:
            if element_type == "paragraph":
                para_index = position_info["index"]
                if para_index < len(self.doc.paragraphs):
                    paragraph = self.doc.paragraphs[para_index]
                    if hasattr(paragraph, 'replace'):
                        paragraph.replace(placeholder, replacement)
                        return True
                    elif hasattr(paragraph, 'text'):
                        # Manual text replacement
                        original_text = paragraph.text
                        if placeholder in original_text:
                            new_text = original_text.replace(placeholder, replacement)
                            paragraph.text = new_text
                            return True

            elif element_type == "table_cell":
                table_idx = position_info["table_index"]
                row_idx = position_info["row"]
                col_idx = position_info["col"]

                if table_idx < len(self.doc.tables):
                    table = self.doc.tables[table_idx]
                    if hasattr(table, 'cell'):
                        cell = table.cell(row_idx, col_idx)
                        if hasattr(cell, 'replace'):
                            cell.replace(placeholder, replacement)
                            return True
                        elif hasattr(cell, 'text'):
                            original_text = cell.text
                            if placeholder in original_text:
                                new_text = original_text.replace(placeholder, replacement)
                                cell.text = new_text
                                return True

        except Exception as e:
            print(f"[Error] Failed to replace at {location_id}: {e}")
            return False

        return False

    def save(self, output_path: str = None) -> None:
        """Save the document using docxedit."""
        save_path = output_path or self.file_path
        if hasattr(self.doc, 'save'):
            self.doc.save(save_path)
        else:
            # Fallback save method
            self.doc.write(save_path)

    def get_text(self) -> str:
        """Get all text from the document using docxedit."""
        if hasattr(self.doc, 'get_text'):
            return self.doc.get_text()
        else:
            # Manual text extraction
            text_parts = []
            for paragraph in self.doc.paragraphs:
                if hasattr(paragraph, 'text'):
                    text_parts.append(paragraph.text)
            return "\n".join(text_parts)
