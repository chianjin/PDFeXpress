# ChangeLog

## 1.0.0

2025-11-02

This software release includes a complete refactoring of the underlying logic and adds some common features.

- **Delete Page**: Delete specified pages from a PDF file.
- **Edit Bookmark**: Edit the bookmark of a PDF file.
- **Extract Images**: Extract images from PDF files.
- **Extract Text**: Extract text from PDF files.
- **Image to PDF**: Convert multiple images into a single PDF file.
- **Interleave PDF**: Interleave pages from two PDF files.
- **Merge Invoice**: Merge multiple Chinese invoice PDFs into one for easy printing.
- **Merge PDF**: Merge multiple PDF files into one.
- **PDF to Image**: Convert PDF pages to images.
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
- `PyMuPDF`upgrade to 1.20.2

## 0.3.3-BETA

2022-06-11

- change compiler to MSVC 2019 on Windows
- fix some bugs in build
- `Nuitka` upgrade to 0.8.4

## 0.3.2-BATE

2022-06-04

- support mouse drag and drop for add files

## 0.3.1-BATE

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

- Nuitka 升级至 0.19.4，添加`-clang -mingw64` 编译选项，使用 `clang` 编译。

## 0.2.1-BETA

2022-01-16

- 增加 Linux/FreeBSD 支持

- 增加主题选择

## 0.2-BETA

2022-01-15

- 增加多语言支持，根据系统语言设置，自动选择界面语言，默认英语。目前支持简体中文。

- 修正`JPEG2000`格式图像的读取、格式转换。

- 改进多进程处理逻辑。

## 0.1.1-BETA

2022-01-11

- 增加多进程支持，提高处理速度。

- 调整程序界面。

## 0.1-BETA

2022-01-10

- 项目发布，具备基本功能，达到可用程度。
