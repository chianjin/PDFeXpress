from toolkit.i18n import gettext_text as _

PAGE_RANGE_SYNTAX_HELP = _(
"""Page Range Syntax Guide

Basic Syntax:
- Comma Separation: 1,3,5 means page 1, 3 and 5
- Hyphen Range: 3-7 means page 3 to 7 (both ends included)
- Omission Range: -10 means from first page to page 10, 5- means from page 5 to last
- Step Syntax: 1-10:2 means from page 1 to 10, one page every 2 pages (1,3,5,7,9)
- Global Step: :3 means from first page to last, one page every 3 pages

Combined Usage:
- Mixed Expression: 1,3-5,7-:2 means page 1, page 3-5, page 7 to last every 2 pages

Multiple Range Groups:
- Semicolon Separation: 1,3,6-9;4-6,8;1-5 means 3 different range groups, will generate 3 PDF files

Duplicates and Reverse:
- Allow Duplicates: + prefix means allow duplicate pages (e.g. +4-8,6,9-12)
- Reverse Range: Reverse is supported in + mode (e.g. +9-5 means reverse from page 9 to 5)

Notes:
- Deduplication is automatic in default mode
- Using reverse range without + mode will cause an error
- All page numbers start counting from 1
"""
)