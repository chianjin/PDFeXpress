from collections import namedtuple
import re

PageSegment = namedtuple('PageSegment', ['pdf_start', 'pdf_end', 'disp_type', 'disp_start'])

def parse_page_format(format_str: str, total_pages: int) -> list[PageSegment]:
    if not format_str:
        return [PageSegment(pdf_start=1, pdf_end=total_pages, disp_type='n', disp_start=1)]

    segments = []
    last_pdf_end = 0
    last_disp = 0

    for seg_str in format_str.split(';'):
        if not seg_str:
            continue
        if ':' in seg_str:
            parts = seg_str.split(':', 1)
            range_str = parts[0].strip()
            disp_str = parts[1].strip()
        else:
            range_str = seg_str.strip()
            disp_str = ''

        # Parse physical range
        pdf_start = last_pdf_end + 1
        pdf_end = total_pages
        if range_str:
            if '-' not in range_str:
                pdf_start = int(range_str)
                pdf_end = pdf_start
            else:
                match = re.match(r'^(\d*)-(\d*)$', range_str)
                if not match:
                    raise ValueError(f"Invalid range: {range_str}")
                start_str, end_str = match.groups()
                if start_str:
                    pdf_start = int(start_str)
                if end_str:
                    pdf_end = int(end_str)

        if pdf_start > pdf_end or pdf_end > total_pages or pdf_start <= last_pdf_end:
            raise ValueError(f"Invalid or overlapping range: {pdf_start}-{pdf_end}")

        # Parse display format
        disp_type = 'n'
        disp_start = last_disp + 1
        if disp_str:
            if disp_str[0].isalpha() and disp_str[0] in 'nrRaA':
                disp_type = disp_str[0]
                disp_str = disp_str[1:]
            if disp_str:
                try:
                    disp_start = int(disp_str)
                except ValueError:
                    raise ValueError(f"Invalid start: {disp_str}")

        segments.append(PageSegment(pdf_start=pdf_start, pdf_end=pdf_end, disp_type=disp_type, disp_start=disp_start))

        # Update last
        page_count = pdf_end - pdf_start + 1
        last_disp = disp_start + page_count - 1
        last_pdf_end = pdf_end

    return segments
