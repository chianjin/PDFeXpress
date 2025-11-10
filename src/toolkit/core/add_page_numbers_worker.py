import queue
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
    q: queue.Queue,
    input_path: str,
    output_path: str,
    rule: str,
    v_pos: str,
    h_pos: str,
    font_name: str,
    font_size: int,
    v_margin: int,
    h_margin: int,
):
    try:
        doc = fitz.open(input_path)
        total_pages = len(doc)
        q.put((0, "Parsing page number rule..."))

        segments = parse_page_format(rule, total_pages)
        
        # Create a map of {page_index: text_to_display}
        page_text_map = {}
        for seg in segments:
            disp_num = seg.disp_start
            for page_num in range(seg.pdf_start, seg.pdf_end + 1):
                text = ''
                if seg.disp_type == 'n':
                    text = str(disp_num)
                elif seg.disp_type == 'r':
                    text = to_roman(disp_num, upper=False)
                elif seg.disp_type == 'R':
                    text = to_roman(disp_num, upper=True)
                elif seg.disp_type == 'a':
                    text = to_alpha(disp_num, upper=False)
                elif seg.disp_type == 'A':
                    text = to_alpha(disp_num, upper=True)
                
                page_text_map[page_num - 1] = text
                disp_num += 1

        q.put((0, f"Adding page numbers to {total_pages} pages..."))

        # Font mapping for fitz
        fitz_font_name = {
            "Courier": "Cour",
            "Times": "TiRo",
            "Helvetica": "HeBo" # Using Bold for better visibility
        }.get(font_name, "HeBo")

        for i, page in enumerate(doc):
            if i in page_text_map:
                text = page_text_map[i]
                page_rect = page.rect
                
                # Vertical position
                if v_pos == 'header':
                    y = v_margin
                else: # footer
                    y = page_rect.height - v_margin - font_size

                # Horizontal position and alignment
                align = fitz.TEXT_ALIGN_CENTER
                if h_pos == 'left':
                    align = fitz.TEXT_ALIGN_LEFT
                    x = h_margin
                elif h_pos == 'right':
                    align = fitz.TEXT_ALIGN_RIGHT
                    x = page_rect.width - h_margin
                elif h_pos == 'center':
                    x = page_rect.width / 2
                elif h_pos == 'outside':
                    if (i + 1) % 2 == 0: # Even page
                        align = fitz.TEXT_ALIGN_LEFT
                        x = h_margin
                    else: # Odd page
                        align = fitz.TEXT_ALIGN_RIGHT
                        x = page_rect.width - h_margin
                elif h_pos == 'inside':
                    if (i + 1) % 2 == 0: # Even page
                        align = fitz.TEXT_ALIGN_RIGHT
                        x = page_rect.width - h_margin
                    else: # Odd page
                        align = fitz.TEXT_ALIGN_LEFT
                        x = h_margin

                # Create rect for textbox
                if align == fitz.TEXT_ALIGN_LEFT:
                    rect = fitz.Rect(x, y, page_rect.width, y + font_size + 5)
                elif align == fitz.TEXT_ALIGN_RIGHT:
                    rect = fitz.Rect(0, y, x, y + font_size + 5)
                else: # Center
                    rect = fitz.Rect(0, y, page_rect.width, y + font_size + 5)

                page.insert_textbox(
                    rect,
                    text,
                    fontname=fitz_font_name,
                    fontsize=font_size,
                    align=align
                )

            progress = int((i + 1) / total_pages * 100)
            q.put((progress, f"Processing page {i + 1}/{total_pages}"))

        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        q.put((100, "Completed"))

    except Exception as e:
        q.put(e)
