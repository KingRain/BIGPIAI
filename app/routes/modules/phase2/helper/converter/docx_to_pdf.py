
import os
import urllib.parse
import pythoncom
import win32com.client
import time


def convert_docx_to_pdf(docx_file: str) -> str:
    """
    Converts a DOCX file to PDF using late-binding (DispatchEx) and numeric constants only.
    This code never imports 'constants' or touches 'gen_py'; it will not trigger COM wrapper generation.
    """
    # 1) Initialize COM on this thread
    # Ensure COM is set up                    :contentReference[oaicite:3]{index=3}
    pythoncom.CoInitialize()

    # 2) Compute output PDF path
    pdf_file = os.path.splitext(docx_file)[0] + ".pdf"
    print(f"PDF file path: {pdf_file}")

    try:
        # 3) Validate the input DOCX path
        normalized_path = os.path.normpath(docx_file)
        decoded_path = urllib.parse.unquote(normalized_path)
        if not os.path.exists(decoded_path):
            raise FileNotFoundError(f"DOCX file not found: {decoded_path}")

        # 4) Ensure output directory exists
        output_folder = os.path.dirname(pdf_file)
        os.makedirs(output_folder, exist_ok=True)

        # 5) Launch Word via DispatchEx (new instance, no gen_py rebuild)
        # New Word COM process   :contentReference[oaicite:4]{index=4}
        word = win32com.client.DispatchEx("Word.Application")
        word.Visible = False
        # wdAlertsNone = 0                               :contentReference[oaicite:5]{index=5}
        word.DisplayAlerts = 0

        # 6) Open the document read-only
        doc = word.Documents.Open(
            decoded_path,
            ReadOnly=True,
            ConfirmConversions=False,
            AddToRecentFiles=False
        )

        # 7) (Optional) Skip updating TOC since that uses doc.TablesOfContents (requires gen_py)
        #    If TOC must be updated, you can do: uncomment next line to update all fields, including TOC
        #    doc.Fields.Update()  # updates all fields (TOC, cross-refs)    :contentReference[oaicite:6]{index=6}

        # 8) Save as PDF using numeric FileFormat=17 (wdFormatPDF = 17)
        doc.SaveAs(os.path.splitext(decoded_path)[0] + ".pdf", FileFormat=17)
        # : contentReference[oaicite:7]{index = 7}

        # 9) Close document and quit Word
        doc.Close(False)   # Close without saving changes
        word.Quit()

        # 10) Let Windows release any file handles
        # Give Word a moment to fully close the file        :contentReference[oaicite:8]{index=8}
        time.sleep(0.5)

        print(f"✅ Converted DOCX to PDF: {pdf_file}")
        return pdf_file

    except Exception as e:
        # If something goes wrong, still try to cleanup
        try:
            doc.Close(False)
        except:
            pass
        try:
            word.Quit()
        except:
            pass
        pythoncom.CoUninitialize()
        raise Exception(
            f"Error converting DOCX to PDF: {e}. Please check the DOCX file and try again.")

    finally:
        # 11) Uninitialize COM on this thread
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    docx_file = "../../input_files/input_document.docx"
    docx_file = os.path.abspath(docx_file)
    convert_docx_to_pdf(docx_file)
