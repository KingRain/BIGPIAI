
from win32com.client import DispatchEx, constants
import win32com
import pythoncom
import os
import win32com.client
import time


def create_docx_start_endpage(input_path: str,
                              start_page: int,
                              end_page: int,
                              output_path: str,
                              title: str,
                              toc_entries: list[dict],
                              dotx_path: str | None) -> None:
    """
    Opens input_path, extracts pages [start_page..end_page], then creates a new DOCX:
      • Page 1 = title (centered, red)
      • Page 2 = a manual TOC (right‐aligned numbers) per toc_entries
      • Pages 3+ = the copied pages from source

    This implementation:
      - Converts paths to absolute.
      - Uses DispatchEx to spawn a fresh Word instance.
      - Never imports 'constants' or iterates 'doc.TablesOfContents'.
      - Updates everything via numeric VB constants only.
    """
    # 1) Convert to absolute paths
    input_path = os.path.abspath(input_path)
    output_path = os.path.abspath(output_path)

    # 2) Remove any stale lock‐files (~$...) next to input/output
    for path in (input_path, output_path):
        lock = os.path.join(os.path.dirname(
            path), "~$" + os.path.basename(path))
        if os.path.exists(lock):
            try:
                os.remove(lock)
            except:
                pass

    # 3) Delete old output file so SaveAs won’t complain
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except PermissionError:
            os.replace(output_path, output_path + ".old")

    # 4) Initialize COM and start Word
    # set up COM for this thread                    :contentReference[oaicite:11]{index=11}
    pythoncom.CoInitialize()
    # brand‐new Word instance :contentReference[oaicite:12]{index=12}
    word = win32com.client.DispatchEx("Word.Application")
    # wdAlertsNone = 0                              :contentReference[oaicite:13]{index=13}
    word.DisplayAlerts = 0
    word.Visible = False

    src = out = None
    try:
        # 5) Open source document read-only
        src = word.Documents.Open(
            input_path,
            ReadOnly=True,
            ConfirmConversions=False,
            AddToRecentFiles=False
        )

        # 6) Determine total pages using numeric WdStatisticPages = 2
        # WdStatisticPages = 2      :contentReference[oaicite:14]{index=14}
        total_pages = src.ComputeStatistics(2)
        if not (1 <= start_page <= total_pages):
            raise ValueError(f"start_page must be between 1 and {total_pages}")
        end_page = min(end_page, total_pages)

        # 7) Copy the requested slice from start_page to end_page
        #    Use numeric WdGoToPage = 1, WdGoToAbsolute = 1
        # position at start_page :contentReference[oaicite:15]{index=15}
        go1 = src.GoTo(What=1, Which=1, Count=start_page)
        if end_page < total_pages:
            go2 = src.GoTo(What=1, Which=1, Count=end_page + 1)
            slice_end = go2.Start - 1
        else:
            slice_end = src.Content.End

        src.Range(Start=go1.Start, End=slice_end).Copy()

        # 8) Build a new document to paste into
        out = word.Documents.Add()
        # Move cursor to beginning of story (WdStory = 6)
        # 6 = wdStory                         :contentReference[oaicite:16]{index=16}
        word.Selection.HomeKey(Unit=6)

        # 8a) Title page: center‐aligned, large red font
        # wdAlignParagraphCenter = 1   :contentReference[oaicite:17]{index=17}
        word.Selection.ParagraphFormat.Alignment = 1
        word.Selection.Font.Size = 36
        word.Selection.Font.Bold = True
        # wdColorRed = 255                      :contentReference[oaicite:18]{index=18}
        word.Selection.Font.Color = 255
        word.Selection.TypeText(title)
        # Reset to default font and left alignment
        word.Selection.Font.Size = 12
        word.Selection.Font.Bold = False
        # wdAlignParagraphLeft = 0    :contentReference[oaicite:19]{index=19}
        word.Selection.ParagraphFormat.Alignment = 0
        # Insert page break (WdPageBreak = 7)
        # 7 = wdPageBreak                       :contentReference[oaicite:20]{index=20}
        word.Selection.InsertBreak(7)

        # 8b) Manual TOC page (right‐aligned numbers using a right tab stop)
        pw = out.PageSetup.PageWidth
        lm = out.PageSetup.LeftMargin
        rm = out.PageSetup.RightMargin
        usable = pw - lm - rm

        pf = word.Selection.ParagraphFormat
        pf.TabStops.ClearAll()
        # 2 = wdAlignTabRight    :contentReference[oaicite:21]{index=21}
        pf.TabStops.Add(Position=usable, Alignment=2)

        # Header “Table of Contents” in bold red
        word.Selection.Font.Bold = True
        word.Selection.Font.Color = 255  # wdColorRed
        word.Selection.TypeText("Table of Contents")
        word.Selection.TypeParagraph()
        # Back to normal font/color
        word.Selection.Font.Bold = False
        word.Selection.Font.Color = 0    # wdColorAutomatic = 0 (black)
        word.Selection.TypeParagraph()

        # Populate each entry: “SectionName [tab] PageNumber”
        for entry in toc_entries:
            sec_name = entry.get("section", "")
            # Calculate relative page: page-number – start_page + 2
            pg_num = entry.get("start_page", 0) - start_page + 3
            word.Selection.TypeText(f"{sec_name}\t{pg_num}")
            word.Selection.TypeParagraph()

        # Insert page break after TOC
        word.Selection.InsertBreak(7)  # wdPageBreak

        # 8c) Paste the copied pages into page 3+
        word.Selection.EndKey(Unit=6)  # Move to end of story (wdStory)
        word.Selection.Paste()

        if (dotx_path):
            # Attach the DOTX template to the new document
            out.AttachedTemplate = os.path.abspath(dotx_path)
            out.UpdateStyles()

        # 9) Save new document (use late-bound SaveAs; no SaveAs2 to avoid requiring gen_py)
        out.SaveAs(output_path)

        # Pause briefly to allow Word to close handles later
        # Let Word release file locks                  :contentReference[oaicite:22]{index=22}
        time.sleep(0.5)

    finally:
        # 10) Ensure both docs are closed, no dialogs
        if out:
            try:
                out.Close(False)
            except:
                pass
        if src:
            try:
                src.Close(False)
            except:
                pass
        # 11) Quit Word and uninitialize COM
        try:
            word.Quit()
        except:
            pass
        pythoncom.CoUninitialize()
