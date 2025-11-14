import queue
from typing import Any
import fitz  # PyMuPDF

from toolkit.util.page_number_parser import parse_page_format

# Helper functions to convert number to different formats
def to_roman(n, upper=True):
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb_lower = ["m", "cm", "d", "cd", "c", "xc", "l", "xl", "x", "ix", "v", "iv", "i"]
    syb_upper = [s.upper() for s in syb_lower]
    syb = syb_upper if upper else syb_lower
    
    roman_num = ''
    i = 0
    while n > 0:
        for _ in range(n // val[i]):
            roman_num += syb[i]
            n -= val[i]
        i += 1
    return roman_num

def to_alpha(n, upper=True):
    alpha_str = ""
    base = ord('A' if upper else 'a')
    while n > 0:
        n, rem = divmod(n - 1, 26)
        alpha_str = chr(base + rem) + alpha_str
    return alpha_str

def add_page_numbers_worker(
    input_path: str,
    output_path: str,
    rule: str,
    v_pos: str,
    h_pos: str,
    font_name: str,
    font_style: str,
    font_size: int,
    v_margin_cm: float,
    h_margin_cm: float,
    cancel_event: Any,
    progress_queue: Any,
    result_queue: Any,
    saving_ack_event: Any,
):
    try:
        # --- 1. Initialization ---
        CM_TO_POINTS = 72 / 2.54
        v_margin_points = v_margin_cm * CM_TO_POINTS
        h_margin_points = h_margin_cm * CM_TO_POINTS

        font_map = {
            ("Courier", "Regular"): "cour", ("Courier", "Bold"): "cobo", ("Courier", "Italic"): "coit", ("Courier", "Bold Italic"): "cobi",
            ("Times", "Regular"): "tiro", ("Times", "Bold"): "tibo", ("Times", "Italic"): "tiit", ("Times", "Bold Italic"): "tibi",
            ("Helvetica", "Regular"): "hero", ("Helvetica", "Bold"): "hebo", ("Helvetica", "Italic"): "heit", ("Helvetica", "Bold Italic"): "hebi",
        }
        fitz_font_name = font_map.get((font_name, font_style), "tiro") # Default to tiro
        font = fitz.Font(fitz_font_name)

        doc = fitz.open(input_path)
        total_pages = len(doc)
        progress_queue.put(("INIT", total_pages))

        # --- 2. Create Page Number Map ---
        segments = parse_page_format(rule, total_pages)
        page_text_map = {}
        for seg in segments:
            disp_num = seg.disp_start
            for page_num in range(seg.pdf_start, seg.pdf_end + 1):
                text = ''
                if seg.disp_type == 'n': text = str(disp_num)
                elif seg.disp_type == 'r': text = to_roman(disp_num, upper=False)
                elif seg.disp_type == 'R': text = to_roman(disp_num, upper=True)
                elif seg.disp_type == 'a': text = to_alpha(disp_num, upper=False)
                elif seg.disp_type == 'A': text = to_alpha(disp_num, upper=True)
                page_text_map[page_num - 1] = text
                disp_num += 1

        # --- 3. Iterate and Insert Text ---
        for i, page in enumerate(doc):
            if cancel_event.is_set():
                result_queue.put(("CANCEL", "Cancelled by user."))
                return

            if i in page_text_map:
                text = page_text_map[i]
                page_rect = page.rect
                text_width = font.text_length(text, fontsize=font_size)

                # Calculate X coordinate
                if h_pos == 'left':
                    x = h_margin_points
                elif h_pos == 'right':
                    x = page_rect.width - text_width - h_margin_points
                elif h_pos == 'center':
                    x = (page_rect.width - text_width) / 2
                elif h_pos == 'outside':
                    x = h_margin_points if (i + 1) % 2 == 0 else page_rect.width - text_width - h_margin_points
                elif h_pos == 'inside':
                    x = page_rect.width - text_width - h_margin_points if (i + 1) % 2 == 0 else h_margin_points
                else:
                    x = (page_rect.width - text_width) / 2 # Default to center

                # Calculate Y coordinate (baseline of the text)
                if v_pos == 'header':
                    y = v_margin_points + font_size
                else:  # footer
                    y = page_rect.height - v_margin_points
                
                page.insert_text((x, y), text, fontname=fitz_font_name, fontsize=font_size)

            progress_queue.put(("PROGRESS", i + 1))

        # --- 4. Save Document ---
        progress_queue.put(("SAVING", "Saving PDF..."))
        saving_ack_event.wait()
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        result_queue.put(("SUCCESS", "Page numbers added successfully."))

    except Exception as e:
        import traceback
        traceback.print_exc()
        result_queue.put(("ERROR", str(e)))
