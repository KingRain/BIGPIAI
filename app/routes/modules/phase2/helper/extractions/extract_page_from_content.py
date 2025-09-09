import re
from ..models import TocEntries
from ..openai_client import client
import os
from ..normalize import format_toccontent_for_tocpage

from thefuzz import fuzz


def extract_page_from_content(page_contents, sections,toc_end_page=None):
    """
    Extract the table of contents from non-TOC pages.
    """
    document_text = format_toccontent_for_tocpage(page_contents, toc_end_page)

    prompt_path = os.path.join(os.path.dirname(
        __file__), "../prompts/extract_page_from_content.txt")

    with open(prompt_path, "r", encoding="utf-8") as f:
        instructions = f.read()

    toc_lines = [f" {i+1}. {entry['section']}" for i,
                 entry in enumerate(sections)]

    toc_block = "- Toc Entries given as:\n" + "\n".join(toc_lines)

    doc_block = "- Document Text given as:\n" + document_text

    try:
        response = client.responses.parse(
            instructions=instructions,
            input=[{"role": "user", "content": f"{toc_block}\n\n{doc_block}"}],
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
        print(
            f"⚠️ Error when extracting the page number for each sections : {e}")
        raise Exception(
            f"Error extracting TOC with GPT: {e}. Please check the PDF content and try again."
        )


def find_section_start_pages(document_pages, toc_entries, threshold=90):
    """
    For each entry in toc_entries (which must have a "section" key),
    find the page where that section title most likely begins by:
      1. Normalizing and counting its words.
      2. On each page, normalizing text, splitting into words, and sliding a window
         of exactly that many words across the page.
      3. Computing fuzz.ratio() between the normalized title and each window string.
      4. Choosing the highest‐scoring page (or exact substring if found).

    Args:
        document_pages (List[Dict[str, Any]]):
            e.g. [ {"page": 0, "text": "…"}, {"page": 1, "text": "…"}, … ]
        toc_entries (List[Dict[str, str]]):
            e.g. [ {"section": "Returnable Schedule 1: Overall capability and experience"}, … ]
        threshold (int):
            The minimum fuzzy ratio (0100) to accept a match.

    Returns:
        List[Dict]:  The same toc_entries list, but each dict now has "start_page": <int> or None.
    """

    def normalize_whitespace(s: str) -> str:
        # Remove newlines, collapse multiple whitespace into a single space, lowercase
        return re.sub(r"\s+", " ", s.replace("\n", " ")).strip().lower()

    for entry in toc_entries:
        raw_title = entry.get("section", "")

        # 1) Normalize title and count its words:
        norm_title = normalize_whitespace(raw_title)
        title_words = re.findall(r"\w+", norm_title)
        n_words = len(title_words)
        if n_words == 0:
            # if an empty or nonsense title, skip matching
            continue

        best_overall_score = 0
        best_overall_page = None

        # 2) For each page, build a list of its normalized words:
        for pg in document_pages:
            page_text = pg.get("text", "")
            norm_page = normalize_whitespace(page_text)
            page_word_list = norm_page.split(" ")

            # If the entire normalized title is a substring of the normalized page,
            # we can assign immediately (this handles exact or whitespace‐only splits).
            if norm_title in norm_page:
                entry["start_page"] = pg["page"]
                break

            # 3) Otherwise, do sliding window of size n_words:
            best_page_score = 0
            word_count = len(page_word_list)

            # Only slide if page has at least n_words
            if word_count >= n_words:
                for i in range(word_count - n_words + 1):
                    window_slice = page_word_list[i: i + n_words]
                    window_text = " ".join(window_slice)
                    score = fuzz.ratio(window_text, norm_title)
                    if score > best_page_score:
                        best_page_score = score

                    # If we hit a perfect 100, no need to scan further windows
                    if best_page_score == 100:
                        break

            # Track the best page‐wide score across all pages
            if best_page_score > best_overall_score:
                best_overall_score = best_page_score
                best_overall_page = pg["page"]

        else:
            # The for–else runs only if we never hit `break` above (no exact substring found)
            if best_overall_score >= threshold:
                entry["start_page"] = best_overall_page

    return toc_entries
