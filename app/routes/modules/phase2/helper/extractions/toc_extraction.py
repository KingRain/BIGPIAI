
import re
import os
import sys
from .extract_toc_endpage import extract_toc_endpage
from models import TocEntries

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def import_custom():
    from openai_client import client
    from normalize import (
        format_content_for_toc_endpage_extraction,
        read_pdf,
        
        format_toc_page_for_extraction,
        format_non_toc_page_for_extraction
    )
    return (
        client,
        format_content_for_toc_endpage_extraction,
        read_pdf,
        format_toc_page_for_extraction,
        format_non_toc_page_for_extraction
    )


client, \
    format_content_for_toc_endpage_extraction, \
    read_pdf, \
    format_toc_page_for_extraction, \
    format_non_toc_page_for_extraction = import_custom()


def extract_toc_from_toc_page(page_contents):
    toc_end_page = extract_toc_endpage(page_contents)

    print(f"TOC ends on page: {toc_end_page}")
    toc_text = format_toc_page_for_extraction(
        page_contents, toc_end_page)

    prompt_path = os.path.join(os.path.dirname(
        __file__), "../prompts/extract_toc_tocpage.txt")

    with open(prompt_path, "r", encoding="utf-8") as f:
        instructions = f.read()

    try:
        response = client.responses.parse(
            model="gpt-4o-mini",
            instructions=instructions,
            input=[
                {"role": "user", "content": toc_text},
            ],
            text_format=TocEntries,
        )

        response_content = response.output_parsed
        return [
            {"section": entry.name, "start_page": int(entry.page_number)}
            for entry in response_content.entries
        ]

    except Exception as e:
        print(f"⚠️ Error extracting TOC from the toc page{e}")
        raise Exception(
            f"Error extracting TOC with GPT: {e}. Please check the PDF content and try again.")


def extract_toc_from_nontoc_content(page_contents):
    """
    Extract the table of contents from non-TOC pages.
    """
    document_text = format_non_toc_page_for_extraction(page_contents)
    prompt_path = os.path.join(os.path.dirname(
        __file__), "../prompts/extract_toc_nontoc.txt")
    # with open("../prompts/extract_toc_nontoc.txt", "r", encoding="utf-8") as f:
    with open(prompt_path, "r", encoding="utf-8") as f:
        instructions = f.read()

    try:
        response = client.responses.parse(
            instructions=instructions,
            input=[{"role": "user", "content": document_text}],
            model="gpt-4o-mini",
            temperature=0,
            text_format=TocEntries,
        )

        response_content = response.output_parsed
        return [
            {"section": entry.name, "start_page": int(entry.page_number)}
            for entry in response_content.entries
        ]

    except Exception as e:
        print(f"⚠️ Error extracting TOC from the non toc content {e}")
        raise Exception(
            f"Error extracting TOC with GPT: {e}. Please check the PDF content and try again."
        )


if __name__ == "__main__":

    pdf_file = "../../input_files/document.pdf"
    pdf_file = os.path.abspath(pdf_file)
    print("path for pdf file is : ", pdf_file)
    page_contents = read_pdf(pdf_file)

    toc_entries_nontoc = extract_toc_from_nontoc_content(
        page_contents)
    print("from the non toc pages : ")
    print(toc_entries_nontoc)
