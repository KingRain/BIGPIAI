# app/cv_processor/config/settings.py
"""
Configuration settings for the CV processing system.
"""
import os
from pathlib import Path

# AI Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")

# File Paths - Dynamic based on Flask app context
def get_project_root():
    """Get project root directory."""
    return Path(__file__).parent.parent.parent.parent

def get_content_dir():
    """Get content directory for CV files."""
    return get_project_root() / "uploads" / "phase3"

def get_templates_dir():
    """Get templates directory."""
    return get_project_root() / "uploads" / "phase3"

def get_output_dir():
    """Get output directory."""
    return get_project_root() / "outputs" / "phase3"

def get_template_path():
    """Get template file path."""
    return get_templates_dir() / "template.docx"

# Legacy constants for backward compatibility
PROJECT_ROOT = get_project_root()
CONTENT_DIR = str(get_content_dir())
TEMPLATES_DIR = str(get_templates_dir())
OUTPUT_DIR = str(get_output_dir())
TEMPLATE_PATH = str(get_template_path())

# JSON output paths
ANALYSIS_JSON_PATH = get_output_dir() / "analysis.json"
SOURCE_PROFILE_JSON_PATH = get_output_dir() / "source_profile.json"
TEMPLATE_SCHEMA_JSON_PATH = get_output_dir() / "template_schema.json"
POSITIONAL_EXECUTION_PLAN_PATH = get_output_dir() / "positional_execution_plan.json"
POSITIONAL_PLACEHOLDERS_PATH = get_output_dir() / "positional_placeholders.json"
POSITION_MAP_PATH = get_output_dir() / "position_map.json"
REPLACEMENT_MAP_PATH = get_output_dir() / "replacement_map.json"

# Processing Configuration
CONCURRENCY = int(os.getenv("CONCURRENCY", "3"))
