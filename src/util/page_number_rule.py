"""Parse the page-numbering rule syntax.

See ``asset/page_number_syntax_guide-zh_CN.txt`` for the full grammar. A rule is a
comma-separated list of segments ``PHYS_RANGE:DISPLAY_FORMAT``:

* ``PHYS_RANGE`` (before the colon, 1-based) selects the pages the segment applies to.
  ``5`` single page, ``5-10`` closed range, ``-10`` from page 1, ``5-`` to last page,
  and empty ``""`` (i.e. ``:...``) means all pages.
* ``DISPLAY_FORMAT`` (after the colon) is ``[type][start]``. Type is one of
  ``n`` (arabic, default), ``r`` (lowercase roman), ``R`` (uppercase roman),
  ``a`` (lowercase letter), ``A`` (uppercase letter). ``start`` is optional:
  explicit (``n10``) starts at 10; omitted (``:R``) continues from the previous
  segment's last value + 1 (or 1 for the first segment); an empty format
  (``6-10:``) resets to arabic starting at 1.
* Later segments override earlier ones for overlapping physical pages.
* Pages not covered by any segment get no page number.

``build_page_number_map(rule, total)`` returns a ``dict`` mapping 1-based page
numbers to their display strings; a page absent from the dict is not numbered.
"""


def _parse_phys_range(expr: str, total: int) -> list[int]:
    """Return a sorted list of 1-based page numbers for one physical range."""
    expr = expr.strip()
    if expr == '':
        return list(range(1, total + 1))
    if '-' in expr:
        lo_s, hi_s = expr.split('-', 1)
        lo = int(lo_s) if lo_s else 1
        hi = int(hi_s) if hi_s else total
        if lo < 1 or hi > total or lo > hi:
            raise ValueError('Invalid page range: %r' % expr)
        return list(range(lo, hi + 1))
    page = int(expr)
    if page < 1 or page > total:
        raise ValueError('Invalid page number: %r' % expr)
    return [page]


def _to_roman(value: int) -> str:
    if value <= 0:
        raise ValueError('Roman numerals require a positive number')
    table = (
        (1000, 'M'),
        (900, 'CM'),
        (500, 'D'),
        (400, 'CD'),
        (100, 'C'),
        (90, 'XC'),
        (50, 'L'),
        (40, 'XL'),
        (10, 'X'),
        (9, 'IX'),
        (5, 'V'),
        (4, 'IV'),
        (1, 'I'),
    )
    out: list[str] = []
    for amount, symbol in table:
        while value >= amount:
            out.append(symbol)
            value -= amount
    return ''.join(out)


def _to_letter(value: int) -> str:
    if value <= 0:
        raise ValueError('Letter numerals require a positive number')
    out = ''
    while value > 0:
        value, rem = divmod(value - 1, 26)
        out = chr(ord('a') + rem) + out
    return out


def _format_number(value: int, type_char: str) -> str:
    if type_char == 'n':
        return str(value)
    if type_char == 'r':
        return _to_roman(value).lower()
    if type_char == 'R':
        return _to_roman(value)
    if type_char == 'a':
        return _to_letter(value)
    if type_char == 'A':
        return _to_letter(value).upper()
    raise ValueError('Unknown number type: %r' % type_char)


def _parse_display_format(fmt: str):
    """Return ``(type_char, start)``; ``start`` is ``None`` for continuation."""
    fmt = fmt.strip()
    if fmt == '':
        return ('n', 1)  # empty format resets to arabic starting at 1
    first = fmt[0]
    if first in ('n', 'r', 'R', 'a', 'A'):
        type_char = first
        num_part = fmt[1:].strip()
    else:
        type_char = 'n'
        num_part = fmt
    if num_part == '':
        return (type_char, None)  # implicit continuation
    try:
        return (type_char, int(num_part))
    except ValueError:
        raise ValueError('Invalid start value in format: %r' % fmt) from None


def build_page_number_map(rule: str, total: int) -> dict[int, str]:
    """Build the 1-based page -> display-string map for ``rule``.

    Raises ``ValueError`` on any malformed segment or out-of-range page.
    """
    if total < 1:
        return {}
    rule = (rule or '').strip()
    if rule == '':
        return {}

    effective: dict[int, str] = {}
    last_value = 0  # running numeric counter for implicit continuation
    for seg in rule.split(','):
        seg = seg.strip()
        if seg == '':
            continue
        if ':' in seg:
            phys_expr, fmt_expr = seg.split(':', 1)
        else:
            # No colon: treat the whole segment as a physical range with an
            # implicit arabic-from-1 format (lenient, matches "1-" style input).
            phys_expr, fmt_expr = seg, ''
        pages = _parse_phys_range(phys_expr.strip(), total)
        type_char, start = _parse_display_format(fmt_expr.strip())
        if start is None:
            start = last_value + 1 if last_value > 0 else 1
        counter = start
        for page in pages:
            effective[page] = _format_number(counter, type_char)
            counter += 1
        last_value = start + len(pages) - 1
    return effective
