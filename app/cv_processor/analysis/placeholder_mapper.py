"""
Placeholder mapping utilities.
"""
from typing import Any, Dict, List

try:
    from jinja2 import Environment, meta
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    Environment = None
    meta = None

from app.cv_processor.analysis.template_analyzer import read_template_full_text
from app.cv_processor.config.settings import get_template_path
from app.cv_processor.utils.ai_client import analyze_with_ai


def map_placeholders_with_ai(template_text: str, allowed_keys: List[str], jinja_placeholders: List[str] = None) -> Dict[str, Any]:
    """Ask AI to map Jinja placeholders to semantic keys from allowed_keys."""
    print("[AI] Starting placeholder mapping (replacement_map)...")
    system = "You are a document template analyst. Return only valid JSON with no commentary."
    keys_str = ", ".join(f"'{k}'" for k in allowed_keys)
    if jinja_placeholders:
        placeholders_str = ", ".join(f"{{{p}}}" for p in jinja_placeholders)
        user_prompt = (
            "You are a document template analyst. I am providing the text from a CV template that uses Jinja placeholders like {{name}}, {{email}}.\n"
            "Your job is to identify what each Jinja placeholder represents based on its context and map it to a specific key from this list: "
            f"[{keys_str}].\n\n"
            "Output a JSON object where:\n"
            "- Keys are semantic field names from the allowed list (create suffixed indices for repeats, e.g., job_title_1).\n"
            "- Values are the placeholder strings found in the template, specifically the Jinja placeholders: {placeholders_str}.\n\n"
            "Only map the provided Jinja placeholders, do not include other placeholders or labels.\n\n"
            "Cover as many relevant fields as possible based on context.\n\n"
            "Here is the template text:\n---\n"
            f"{template_text[:16000]}\n---"
        )
    else:
        user_prompt = (
            "You are a document template analyst. I am providing the text from a CV template that may use vague placeholders like 'xxx' or '[insert ...]'.\n"
            "Your job is to identify what each placeholder represents based on its context and map it to a specific key from this list: "
            f"[{keys_str}].\n\n"
            "Output a JSON object where:\n"
            "- Keys are semantic field names from the allowed list (create suffixed indices for repeats, e.g., job_title_1).\n"
            "- Values are the placeholder strings found in the template (e.g., 'xxx', '[insert detail]').\n\n"
            "Cover as many relevant fields as possible based on context.\n\n"
            "Here is the template text:\n---\n"
            f"{template_text[:16000]}\n---"
        )

    result = analyze_with_ai(user_prompt, system)
    print("[AI] Placeholder mapping complete.")
    return result


def map_jinja_placeholders_to_values(jinja_placeholders: List[str], resume_text: str, template_text: str) -> Dict[str, str]:
    """Map Jinja placeholders to appropriate values from resume content, using template context."""
    system = "You are an expert data extractor. Return only valid JSON with no commentary."
    placeholders_str = "\n".join(f"- {{{p}}}" for p in jinja_placeholders)
    user_prompt = (
        "I have a CV template with Jinja placeholders and the full text content of a resume.\n\n"
        f"Template Text (shows context around placeholders):\n---\n{template_text[:10000]}\n---\n\n"
        f"Resume Content:\n---\n{resume_text[:8000]}\n---\n\n"
        "Placeholders to fill:\n"
        f"{placeholders_str}\n\n"
        "For each placeholder in the template, extract the most appropriate value from the resume content. Consider the context and labels around the placeholder in the template (e.g., if it's near 'Participant/Named Sub-contractor:', extract subcontractor info).\n\n"
        "For tables in the template, use the table structure and surrounding text to extract relevant data.\n\n"
        "Format lists like qualifications, achievements, or similar as bullet points using the • symbol for each item.\n\n"
        "Keep overview and summary content concise and to the point, typically 100-200 words.\n\n"
        "For questions about project commitments, availability, timelines, or percentage of time, look for information about current projects, procurement phases, delivery timelines, and time commitments in the resume.\n\n"
        "Avoid duplicating content across different placeholders. Provide unique and varied information for each section - for example, 'role and tasks' should differ from 'key achievements'.\n\n"
        "For specific fields like 'Participant/Named Sub-contractor', search for subcontractor, partnership, or collaborative project information in the resume.\n\n"
        "Make sure the extracted values are appropriate in length and detail for the context - not too long or short. Include summaries, achievements, and other relevant content.\n\n"
        "Output a JSON object where:\n"
        "- Keys are the placeholder names (without {{ }})\n"
        "- Values are the extracted data strings, or 'N/A' if no appropriate value can be found\n\n"
        "If a placeholder cannot be filled, use 'N/A'."
    )
    result = analyze_with_ai(user_prompt, system)
    return result


def extract_jinja_placeholders(template_text: str) -> List[str]:
    """Extract Jinja placeholders from template text."""
    if not JINJA2_AVAILABLE:
        raise RuntimeError("jinja2 package not installed. Run: pip install jinja2")
    env = Environment()
    ast = env.parse(template_text)
    variables = meta.find_undeclared_variables(ast)
    return list(variables)
