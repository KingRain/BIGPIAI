# app/cv_processor/utils/ai_client.py
"""
Unified AI client supporting Gemini API.
"""
import os
import json
from typing import Dict, Any, List

# Import Gemini AI library
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

from app.cv_processor.config.settings import AI_PROVIDER, MODEL_NAME
from app.cv_processor.utils.env_utils import load_env_from_file


class AIClient:
    """Unified AI client using Gemini API."""

    def __init__(self, provider: str = AI_PROVIDER):
        self.provider = provider

        # Load environment variables from .env file
        load_env_from_file()

        if provider == "gemini":
            if not GEMINI_AVAILABLE:
                raise RuntimeError("google-generativeai package not installed. Run: pip install google-generativeai")
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise RuntimeError("GEMINI_API_KEY environment variable not set.")
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(MODEL_NAME)

        else:
            raise ValueError(f"Unsupported AI provider: {provider}. Use 'gemini' only")

    def generate(self, messages: list, temperature: float = 0.0) -> str:
        """Generate chat completion using Gemini API."""

        if self.provider == "gemini":
            # Convert messages to Gemini format
            prompt_parts = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                if role == "system":
                    prompt_parts.append(f"System: {content}")
                elif role == "user":
                    prompt_parts.append(f"User: {content}")
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}")

            prompt = "\n\n".join(prompt_parts)

            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=8192,
            )

            response = self.client.generate_content(
                prompt,
                generation_config=generation_config
            )

            return response.text

        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from AI response, handling code blocks and malformed JSON."""
        text = response_text.strip()

        # Remove code block markers
        if text.startswith("```"):
            lines = [ln for ln in text.splitlines() if not ln.strip().startswith("```")]
            text = "\n".join(lines)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON within the text
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(text[start:end + 1])
                except json.JSONDecodeError:
                    pass

            # Try to find JSON array - with better handling for truncated responses
            start = text.find("[")
            if start != -1:
                # Look for the last complete object in the array
                bracket_count = 0
                brace_count = 0
                last_complete_pos = start

                for i, char in enumerate(text[start:], start):
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            # Found complete array
                            try:
                                return json.loads(text[start:i + 1])
                            except json.JSONDecodeError:
                                pass
                    elif char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and bracket_count == 1:
                            # Found complete object within array
                            last_complete_pos = i

                # If array is incomplete, try to extract up to last complete object
                if last_complete_pos > start:
                    # Find the last comma before the incomplete object
                    partial_text = text[start:last_complete_pos + 1]
                    # Add closing bracket if missing
                    if not partial_text.rstrip().endswith(']'):
                        partial_text = partial_text.rstrip().rstrip(',') + ']'
                    try:
                        return json.loads(partial_text)
                    except json.JSONDecodeError:
                        pass

            raise RuntimeError(f"Could not extract valid JSON from AI response: {text[:500]}...")


def get_ai_client() -> AIClient:
    """Get configured AI client instance."""
    return AIClient()


# Convenience functions for backward compatibility
def analyze_with_ai(user_prompt: str, system_prompt: str = "", temperature: float = 0.0) -> Dict[str, Any]:
    """Analyze content using Gemini AI."""
    client = get_ai_client()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.generate(messages, temperature)
    result = client.extract_json_from_response(response)

    return result


def parse_with_ai(text: str, instructions: str, temperature: float = 0.0) -> dict:
    """Parse text using Gemini AI with specific instructions."""
    system_prompt = "You are an expert data parser. Return only valid JSON with no commentary."
    prompt = f"{instructions}\n\nText to parse:\n{text}"

    result = analyze_with_ai(prompt, system_prompt, temperature)
    return result
