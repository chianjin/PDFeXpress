# ChangeLog

## 2.0

2026-08-16

### Feature Groups

Four new features added (Encrypt, Decrypt, Compress, Add Watermark), bringing the total to 18 features across 7 groups.

- **Document Assembly**
    - **Merge PDF**: No change.
    - **Interleave PDF**: No change.
    - **Split PDF**: No change.
    - **Rotate PDF**: No change.
    - **Delete Pages**: No change.

- **Content Extraction**
    - **Extract Text**: No change.
    - **Extract Images**: No change.

- **Format Conversion**
    - **Images to PDF**: No change.
    - **PDF to Images**: No change.
    - **PDF to Long Image**: No change.

- **Document Compression**
    - **Quick Compress** (new): Compress multiple PDFs one-to-one using the built-in cleanup pipeline (no embedded-image re-encoding).
    - **Deep Compress** (new): Compress a single PDF page by page, re-encoding embedded images for maximum reduction.

- **Page Annotation**
    - **Add Page Numbers**: No change.
    - **Add Watermark** (new): Overlay a text watermark on PDF pages.
    - **Edit Bookmarks**: No change.

- **Document Security**
    - **Encrypt PDF** (new): Encrypt a PDF with a password.
    - **Decrypt PDF** (new): Remove password protection from a PDF.

- **Invoice Processing**
    - **Merge Invoices**: No change.

## 1.1.0

2025-11-15

- Add "Add Page Numbers" feature.
- Unify PDF library import to `pymupdf`.
- Clean up source code comments.

## 1.0.0

2025-11-02

This software release includes a complete refactoring of the underlying logic and adds some common features.

- **Delete Pages**: Delete specified pages from a PDF file.
- **Edit Bookmarks**: Edit the bookmarks of a PDF file.
- **Extract Images**: Extract images from PDF files.
- **Extract Text**: Extract text from PDF files.
- **Images to PDF**: Convert multiple images into a single PDF file.
- **Interleave PDF**: Interleave pages from two PDF files.
- **Merge Invoices**: Merge multiple Chinese invoice PDFs into one for easy printing.
- **Merge PDF**: Merge multiple PDF files into one.
- **PDF to Images**: Convert PDF pages to images.
- **PDF to Long Image**: Convert all PDF pages into a single long image.
- **Rotate PDF**: Rotate pages in a PDF file.
- **Split PDF**: Split a PDF file into multiple documents.

## 0.4.2-BETA

2025-10-10

- fix `pdf_to_image.py` bugs
- add `bake()` for pages in `merge_invoice.py`
- use `pyinstaller` instead of `nuitka`

## 0.4.1.2-BETA

2025-01-09

- fix `merge_invoice.py` bugs

## 0.4.1.1-BETA

2024-12-26

- fix bugs

## 0.4.1-BETA

2024-12-18

- Add `PDF to Long Image` function
- Add `Edit TOC` function
- Add `Generate TOC` option for `Merge PDF`

## 0.4-BETA

2024-12-13

- Remove `Compress PDF` function
- Add `Merge Invoice` function
- Remove Windows x86 support
- Switch to MingW64/Clang compiler
- Python update to 3.11
- PyMuPDF update to 1.22.5
- Pillow update to 11.0.0
- Nuitka update to 1.8.6

## 0.3.4-BETA

2022-09-3

- fix few bugs
- `Nuitka` upgrade to 1.0.6
- `PyMuPDF` upgrade to 1.20.2

## 0.3.3-BETA

2022-06-11

- change compiler to MSVC 2019 on Windows
- fix some bugs in build
- `Nuitka` upgrade to 0.8.4

## 0.3.2-BETA

2022-06-04

- support mouse drag and drop for add files

## 0.3.1-BETA

2022-06-04

- compatible with Python 3.8 and later
- support Windows 7 and higher
- build 32bit binary and portable package

## 0.3-BATE

2022-04-13

- Support batch rotation of multiple PDF files.

## 0.2.2-BETA

2022-01-23

- Improved verification of the values of the options.
- `Nuitka` upgraded to 0.19.4, added `-clang -mingw64` compilation option, and compiled with `clang`.

## 0.2.1-BETA

2022-01-16

- Added Linux/FreeBSD support.
- Added `tkinter` theme selection.

## 0.2-BETA

2022-01-15

- Added multi-language support, automatically select interface language according to system language settings, default
  English. Chinese Simplified are currently supported.
- Fixed `JPEG2000` format image reading, format conversion.
- Improved multi-process processing logic.

## 0.1.1-BETA

2022-01-11

- Add `multiprocess` support to improve processing speed.
- Improve program interface.

## 0.1-BETA

2022-01-10

- The project is published, with basic functions, to a usable level.