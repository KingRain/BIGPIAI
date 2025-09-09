# Add the parent directory to sys.path
import os
import sys
from ..openai_client import client
from pydantic import BaseModel, Field

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def import_custom():
    from ..normalize import format_content_for_toc_endpage_extraction
    return format_content_for_toc_endpage_extraction


format_content_for_toc_endpage_extraction = import_custom()


class TocEndPageModel(BaseModel):
    # Pydantic will coerce numeric strings to int. If the model sees “-1” or “3”, it becomes int.
    toc_end_page: int = Field(...,
                              description="0-based index where TOC ends")


def extract_toc_endpage(page_contents):
    # First, format the page contents in whatever way your helper expects.
    page_contents = format_content_for_toc_endpage_extraction(page_contents)

    with open(os.path.join(os.path.dirname(__file__), "../prompts/extract_toc_endpage.txt"), "r", encoding="utf-8") as f:
        instructions = f.read()

    try:
        response = client.responses.parse(
            model="gpt-4o-mini",
            instructions=instructions,
            input=[{"role": "user", "content": page_contents}],
            text_format=TocEndPageModel,
        )

        end_page = response.output_parsed.toc_end_page

        # Ensure the raw_value is an integer
        if not isinstance(end_page, int):
            raise ValueError(f"Expected integer, got: {end_page!r}")

        if end_page < 0:
            raise ValueError(
                "GPT could not determine a valid TOC end page (returned -1).")

        return end_page

    except Exception as e:
        print(f"⚠️ Error detecting TOC end page: {e}")
        raise Exception(
            f"Error detecting TOC end page: {e}. Please check the PDF content and try again."
        )
