# cv_processor/core/__init__.py
"""
Core CV processing functionality.
"""
from app.cv_processor.analysis.cv_parser import (
    parse_resume_with_ai,
    build_structured_cv_json,
    extract_raw_cv_text,
    get_raw_cv_text
)
from app.cv_processor.analysis.template_analyzer import (
    analyze_template_schema,
    read_template_full_text,
    build_allowed_keys_from_resume
)
from app.cv_processor.analysis.placeholder_mapper import (
    map_placeholders_with_ai,
    map_jinja_placeholders_to_values,
    extract_jinja_placeholders
)

__all__ = [
    # CV Analysis
    'parse_resume_with_ai',
    'build_structured_cv_json',
    'extract_raw_cv_text',
    'get_raw_cv_text',

    # Template Analysis
    'analyze_template_schema',
    'read_template_full_text',
    'build_allowed_keys_from_resume',

    # Placeholder Mapping
    'map_placeholders_with_ai',
    'map_jinja_placeholders_to_values',
    'extract_jinja_placeholders',
]
