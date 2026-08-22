# PDF eXpress

[[English]](https://github.com/chianjin/PDFeXpress/blob/main/README.md)  [[简体中文]](https://github.com/chianjin/PDFeXpress/blob/main/README.zh_CN.md)

**PDF eXpress** is a Python-based application for PDF file operations.

## Development Environment

- Python 3.14
- pymupdf==1.28.2
- pillow==12.3.0
- tkinterdnd2==0.6.2
- pyinstaller==6.22.1
- babel==2.18.0

## Current Version

The current version is 2.0, which has been tested on Windows 11 AMD64 and Ubuntu 25.10 x86_64.

## Main Functions

**Document Assembly**

* **Merge PDF**: Merge multiple PDF files into one
* **Interleave PDF**: Interleave pages from two PDF files
* **Split PDF**: Split one PDF to several, supporting single-page splitting, by page count, by copy count, and by range
* **Divide Pages**: Divide PDF pages into multiple parts by direction (vertical/horizontal) and count
* **Rotate PDF**: Rotate each page by 90°, 180°, and 270° clockwise
* **Delete Pages**: Delete specified pages from a PDF file

**Content Extraction**

* **Extract Text**: Extract plain text from PDF files without formatting
* **Extract Images**: Extract images from PDF files and save them in original format

**Format Conversion**

* **Images to PDF**: Convert images to one PDF
* **PDF to Images**: Convert each page to image
* **PDF to Long Image**: Convert each page to image and merge into a long image

**Document Compression**

* **Quick Compress**: Compress multiple PDFs one-to-one with the built-in cleanup pipeline
* **Deep Compress**: Compress a single PDF page by page, re-encoding embedded images for maximum reduction

**Page Annotation**

* **Add Page Numbers**: Add page numbers to a PDF file with various formatting options
* **Add Watermark**: Add a watermark to PDF pages
* **Edit Bookmarks**: Edit the bookmarks of a PDF file

**Document Security**

* **Encrypt PDF**: Encrypt a PDF with a user/owner password
* **Decrypt PDF**: Remove password protection from a PDF

**Invoice Processing**

* **Merge Invoices**: Merge multiple Chinese invoice PDFs into one for easy printing

## Running Method

**Important for Windows Users:** If you are upgrading from a version older than 1.0.0, please uninstall the previous version manually before installing this one to avoid potential conflicts.

There are two types of pre-compiled packages, installers and portable packages. [Download](https://github.com/chianjin/PDFeXpress/releases) and install or unzip it, run `PDFeXpress.exe`.

You can also download from: [Quark Cloud Drive](https://pan.quark.cn/s/abc772612ee5?pwd=97sh) [Baidu Cloud Drive](https://pan.baidu.com/s/14I_0RdbfVqpWORXfgYlEjQ?pwd=i4xb)

## Build

If you want to build the application yourself, follow these steps:

### Prerequisites

This project supports internationalization. Translation catalogs are managed with [Babel](https://babel.pocoo.org/) (listed in `requirements-dev`). The `i18n.py` script wraps the pybabel commands (`-e` extract / `-u` update / `-c` compile / `-a` all); running the build compiles the `.po` files to `.mo`.

### Procedure

```shell
> git clone https://github.com/chianjin/PDFeXpress.git
> cd PDFeXpress
> pip install -r requirements-dev
> python i18n.py -c
> python build.py
```

> **Note**: `python i18n.py -c` (i.e. `pybabel compile`) skips a catalog whose header carries the `#, fuzzy` flag. If the Chinese catalog is not compiled, remove that flag from `src/locale/zh_CN/LC_MESSAGES/pdfexpress.po` first.
>
> **Note**: `setup_remotes.py` is for this repository only — it configures dual push to both Gitee and GitHub. **Do not run it on a fork**, otherwise your push URLs will point to this project's remotes.

Precompiled package and installer are saved in the `release` directory.

**Note**: Installer will auto build on Windows, if [Inno Setup](https://jrsoftware.org/isinfo.php) installed.

## License

Copyright (c) 2026 chian.jin@gmail.com.

This project is licensed under the GNU Affero General Public License Version 3.
See the [LICENSE](LICENSE) file for full details.

## Third-Party Acknowledgements

This project utilizes several third-party libraries. The following is a list of these libraries and their respective licenses and homepages/source code.

| Library     | License                                                                                               | Homepage/Source                                                       |
| ----------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Python      | [Python Software Foundation License](https://docs.python.org/3/license.html)                          | [python.org](https://www.python.org/)                                 |
| PyMuPDF     | [GNU AGPLv3](https://www.gnu.org/licenses/agpl-3.0.en.html)                                           | [PyMuPdf - GitHub](https://github.com/pymupdf/PyMuPDF)                |
| Pillow      | [Pillow License (MIT-CMU)](https://github.com/python-pillow/Pillow/blob/main/LICENSE)                 | [python-pillow.org](https://python-pillow.org/)                       |
| tkinterdnd2 | [MIT License](https://github.com/pmgagne/tkinterdnd2/blob/master/LICENSE)                             | [pypi.org/project/tkinterdnd2](https://pypi.org/project/tkinterdnd2/) |
| PyInstaller | [GPL 2.0 with linking exception](https://github.com/pyinstaller/pyinstaller/blob/develop/LICENSE.txt) | [pyinstaller.org](https://pyinstaller.org/)                           |

The application is built using PyInstaller, which has a special license that allows for the distribution of bundled applications (including commercial ones) without being subject to the GPL.