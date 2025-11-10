from toolkit.i18n import gettext_text as _

PAGE_NUMBER_SYNTAX_HELP = _(
"""Page Range Syntax Guide

1. Structure:
   - Use ';' to separate different formatting segments.
   - e.g., "1-4:R;5-:"

2. Physical Page Range (before ':'):
   - 1-based index for pages.
   - "5-": Page 5 to end.
   - "-10": Page 1 to 10.
   - "5": Only page 5.
   - Omit for all pages or remaining pages.

3. Display Format (after ':'):
   - Format: [Type][StartValue], e.g., R1, n5.
   - Types: n (number), r (lowercase roman), R (uppercase roman), a (lowercase letter), A (uppercase letter).
   - StartValue: Integer to start counting from.
   - If omitted, defaults to 'n' and continues from the previous segment or starts at 1.

4. Examples (for a 30-page PDF):
   - "": All pages numbered 1-30.
   - ":10": All pages numbered 10-39.
   - "1-4:R;5-:": Pages 1-4 as I-IV, pages 5-30 as 5-30.
   - "1-4:R;5-6:r1;7-:1": Pages 1-4 as I-IV, 5-6 as i-ii, 7-30 as 1-24.
"""
)