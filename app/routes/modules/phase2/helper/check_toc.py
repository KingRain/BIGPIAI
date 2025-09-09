

from openai_client import client
from normalize import format_content_for_toc_check


def check_toc_in_pdf(pdf_content):

    pdf_content = format_content_for_toc_check(pdf_content)
    if not pdf_content:
        return False

    # Define the prompt for ChatGPT
    prompt = (
        "You are a helpful assistant. Analyze the following PDF content and determine if it contains a Table of Contents. "
        "The Table of Contents may be written in other meaningful words like 'Index', 'Contents', or similar. "
        "Respond with 'true' if it exists, otherwise respond with 'false'.\n\n"
        f"PDF Content:\n{pdf_content}"
    )

    try:

        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-4o-mini",
            max_tokens=10,
            temperature=0
        )

        # Extract the response text
        result = response.choices[0].message.content.strip().lower()
        return result == "true"
    except Exception as e:
        raise Exception(
            f"Error checking TOC in PDF: {e}. Please check the PDF content and try again."
        )
    
