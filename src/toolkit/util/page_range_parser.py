"""Range parsing utility module for PDF page operations."""

from typing import List
from toolkit.i18n import gettext_text as _


def _parse_range(range_string: str, total_pages: int) -> List[int]:
    """Parse a single range expression: 1-9:3"""
    chunk: List[int] = []

    step = 1
    range_part = range_string

    if ":" in range_string:
        range_part, step_part = range_string.rsplit(":", 1)
        step = int(step_part)

        if range_part == "":
            return list(range(0, total_pages, step))

    if "-" in range_part:
        if range_part.startswith("-") and range_part.count("-") == 1:
            start = 1
            end = int(range_part[1:])
        elif range_part.endswith("-") and range_part.count("-") == 1:
            start = int(range_part[:-1])
            end = total_pages
        else:
            start_str, end_str = range_part.split("-", 1)
            start = int(start_str)
            end = int(end_str)

            if start > end:
                return list(range(start - 1, end - 2, -step))

        if start < 1 or end > total_pages:
            raise ValueError(
                _("Invalid range '{part}': must be between 1-{total_pages}.").format(
                    part=range_string, total_pages=total_pages
                )
            )

        chunk = list(range(start - 1, end, step))
    else:
        page = int(range_part)
        if page < 1 or page > total_pages:
            raise ValueError(
                _("Invalid page '{part}': must be between 1-{total_pages}.").format(
                    part=range_string, total_pages=total_pages
                )
            )
        chunk = [page - 1]

    return chunk


def _parse_ranges_without_duplicates(range_string: str, total_pages: int) -> List[int]:
    """Parse range group: 3,1-6,10-:2"""
    chunk: List[int] = []
    seen = set()

    for range_part in range_string.split(","):
        range_part = range_part.strip()
        if not range_part:
            continue

        range_pages = _parse_range(range_part, total_pages)

        for page in range_pages:
            if page not in seen:
                seen.add(page)
                chunk.append(page)

    return chunk


def _parse_ranges_with_duplicates(range_string: str, total_pages: int) -> List[int]:
    """Parse range group allowing duplicates: +9,12-5,7,12-:3"""
    chunk: List[int] = []

    if range_string.startswith("+"):
        range_string = range_string[1:].strip()

    for range_part in range_string.split(","):
        range_part = range_part.strip()
        if not range_part:
            continue

        chunk.extend(_parse_range(range_part, total_pages))

    return chunk


def parse_page_ranges(
    range_string: str, total_pages: int, allow_duplicates: bool = True
) -> List[List[int]]:
    chunks: List[List[int]] = []

    for range_group in range_string.split(";"):
        range_group = range_group.strip()
        if not range_group:
            continue

        if range_group.startswith("+"):
            if allow_duplicates:
                chunks.append(_parse_ranges_with_duplicates(range_group, total_pages))
            else:
                raise ValueError(_("Duplicates are not allowed"))
        else:
            chunks.append(_parse_ranges_without_duplicates(range_group, total_pages))

    return chunks
