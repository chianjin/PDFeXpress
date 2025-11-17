from toolkit.i18n import gettext_text as _

PAGE_NUMBERING_FORMAT = {
    'title': _('Page Numbering Format Syntax Guide'),
    'brief': _(
        'Default: Continuous numbering starting at 1. Click "Help" button for more detail.'
    ),
    'content': _(
        """        Page Numbering Format Syntax Guide

1. Structure
   - Use semicolon (;) to separate different page range segments. 
   - Segment Format: [Physical Page Range]:[Display Format]. E.g., "1-4:R;5-:". 

2. Physical Page Range (Before :)
   - Physical page number: 1-based index. 
   - Range: start - end 
     5-: Page 5 to the last page. 
     -10: Page 1 to page 10. 
     5: Only page 5.
   - Omission:
     Omit the start index (e.g., -10) to begin at page 1.
     Omit the end index (e.g., 5-) to end at the last page. 
     Omit the entire range (e.g., :R1) to apply the format to all pages. 

3. Display Format (After :)
   - Format: [Type][StartValue] (optional). E.g., R1, n5. 
   - Types (Case-Sensitive): 
     n: Arabic numbers (1, 2, 3...)
     r: Lowercase Roman numerals (i, ii, iii...)
     R: Uppercase Roman numerals (I, II, III...)
     a: Lowercase letters (a, b, c...)
     A: Uppercase letters (A, B, C...)
   - StartValue: An integer specifying the number to begin counting from. 
   - Default Behavior:
     If Type is omitted, it defaults to 'n' (Arabic numbers). 
     If StartValue is omitted, it continues sequentially from the previous segment's end page number, or starts at 1 if this is the first segment with an omitted StartValue. 

4. Examples (for a 30-page PDF)
   - "": All pages are numbered 1-30. 
   - ":10": All pages (1-30) are numbered starting from 10 (i.e., display 10-39). 
   - "1-4:R;5-:": Pages 1-4 use uppercase Roman numerals (I-IV), pages 5-30 continue numbering sequentially (5-30). 
   - "1-4:R;5-6:r1;7-:1": 
     Pages 1-4 as I-IV. 
     Pages 5-6 use lowercase Roman starting at i. 
     Pages 7-30 use Arabic numbers starting at 1.
"""
    ),
}

PAGE_RANGE_SELECTION = {
    'title': _('Page Range Selection Syntax Guide'),
    'brief': _('Example: 3,7-9,12;:2. Click "Help" button for more description.'),
    'content': _(
        """        Page Range Selection Syntax Guide

1. Basic Selection and Range Definition
   - Comma Separation (,): Separates individual page numbers or ranges. 
     Example: 1,5,10    Result: (1, 5, 10)
   - Hyphen Range (-): Defines a consecutive range, including both start and end pages.
     Example: 3-7   Result: (3, 4, 5, 6, 7)
   - Omission Start (-N): Selects pages from the first page (1) up to page N.
     Example: -10   Result: (1, 2, ..., 10)
   - Omission End (N-): Selects pages from page N up to the last page.
     Example: 5-    Result: (5, 6, ..., Last)

2. Step and Skip Syntax
   Use the colon (:) to specify the step interval within a range.
   - Step Syntax (A-B:S): Selects pages from A to B, choosing one page every S pages.
     Example: 1-10:2    Result: (1, 3, 5, 7, 9)
   - Global Step (:S): Applies the step S to the entire document range (from first to last page).
     Example: :3    Result: (1, 4, 7, 10, ...)

3. Combination and Output Control
   - Mixed Expression: Various syntax combinations connected by commas.
     Example: 1,3-5,7-:2    Result: (1, 3, 4, 5, 7, 9, 11, ...)
   - Semicolon Separation (;): Multiple File Output. Semicolons separate distinct range groups; each group will generate a separate PDF file.
     Example: 1-5;8,10- Result: File 1: (1, 2, 3, 4, 5); File 2: (8, 10, 11, ..., Last)

4. Special Mode: Duplicates and Reverse (+ Mode), only for Split PDF
   Adding the prefix + activates a special mode that allows for duplicate pages and reverse selection.
   - Allow Duplicates (+ Prefix): Disables automatic deduplication, allowing page numbers to appear multiple times.
     Example: +4-8,6,9  Result: (4, 5, 6, 7, 8, 6, 9)
   - Reverse Range (+N-M where N>M): Supported only in + mode. Selects pages in descending order from N to M.
     Example: +9-5  Result: (9, 8, 7, 6, 5)

5. Important Notes
   - Deduplication: In the default mode (without the + prefix), the system automatically removes all duplicate page numbers.
   - Page Start: All page numbers start counting from 1.
   - Reverse Error: Using a reverse range (e.g., 9-5) in the default mode will result in an error.
"""
    ),
}
