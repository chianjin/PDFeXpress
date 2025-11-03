# toolkit/core/delete_pages_worker.py
from pathlib import Path
from typing import Set

import pymupdf

from toolkit.i18n import gettext_text as _, ngettext


def _parse_pages_to_delete(range_string: str, total_pages: int) -> Set[int]:
    pages_to_delete_set: Set[int] = set()
    if not range_string:
        return pages_to_delete_set

    parts = range_string.split(',')
    for part in parts:
        part = part.strip()
        if not part:
            continue
        try:
            if '-' in part:
                start_str, end_str = part.split('-', 1)
                start = int(start_str.strip())
                end = int(end_str.strip())
                if not (1 <= start <= end <= total_pages):
                    raise ValueError(_("Invalid page range '{part}': must between 1-{total_pages}.").format(part=part,
                                                                                                          total_pages=total_pages))
                current_range_set = set(range(start - 1, end))
                if not current_range_set.isdisjoint(pages_to_delete_set):
                    raise ValueError(_("Overlapping page range detected: '{part}'.").format(part=part))
                pages_to_delete_set.update(current_range_set)
            else:
                page = int(part)
                if not (1 <= page <= total_pages):
                    raise ValueError(_("Invalid page '{part}': must between 1-{total_pages}.").format(part=part,
                                                                                                         total_pages=total_pages))
                if (page - 1) in pages_to_delete_set:
                    raise ValueError(_("Duplicate page detected: '{part}'.").format(part=part))
                pages_to_delete_set.add(page - 1)
        except ValueError as ve:
            raise ve
        except Exception as e:
            raise ValueError(_("Invalid page range format '{part}': {e}").format(part=part, e=str(e)))

    return pages_to_delete_set


def delete_pages_worker(
        pdf_path,
        output_path,
        pages_to_delete_str,
        cancel_event,
        progress_queue,
        result_queue,
        saving_ack_event
):
    try:
        if not pages_to_delete_str:
            raise ValueError(_("No pages specified to delete."))

        with pymupdf.open(pdf_path) as doc:
            total_pages_doc = len(doc)
            if total_pages_doc == 0:
                raise ValueError(_("PDF file has no pages."))

            progress_queue.put(("INIT", 100))

            pages_to_delete_set = _parse_pages_to_delete(pages_to_delete_str, total_pages_doc)
            if not pages_to_delete_set:
                raise ValueError(_("No valid pages could be parsed from '{pages_to_delete_str}'.").format(
                    pages_to_delete_str=pages_to_delete_str))

            progress_queue.put(("PROGRESS", 50))

            pages_to_keep = [p for p in range(total_pages_doc) if p not in pages_to_delete_set]
            if not pages_to_keep:
                raise ValueError(
                    _("Will delete all pages from {pdf_path_name}.").format(
                        pdf_path_name=Path(pdf_path).name))

            doc.select(pages_to_keep)

            progress_queue.put(("SAVING", _("Saving PDF...")))
            while not saving_ack_event.is_set():
                if cancel_event.is_set():
                    result_queue.put(("CANCEL", _("Cancelled by user.")))
                    return
                saving_ack_event.wait(timeout=0.1)

            doc.save(output_path, garbage=4, deflate=True)

        progress_queue.put(("PROGRESS", 100))

        success_msg = ngettext(
            "Deleted {} page.",
            "Deleted {} pages.",
            len(pages_to_delete_set)
        ).format(len(pages_to_delete_set))
        result_queue.put(("SUCCESS", success_msg))

    except Exception as e:
        result_queue.put(("ERROR", _("Unexpected error occurred: {}").format(e)))
