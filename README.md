# PDF Express

[[English]](https://github.com/chianjin/PDFeXpress/blob/main/README.md)  [[Simplified Chinese]](https://github.com/chianjin/PDFeXpress/blob/main/README.zh_CN.md)

**PDF Express** is a Python-based application for PDF file operations.

## Development Environment

- Python 3.13
- PyMuPDF==1.26.5
- pillow==12.0.0
- tkinterdnd2==0.4.3
- pyinstaller==6.16.0

## Current Version

The current version is 1.1.0, which has been tested on 64-bit Windows 11.

## Main Functions

* **Merge PDF**: Merge multiple PDF files into one
* **Interleave PDF**: Interleave pages from two PDF files
* **Split PDF**: Split one PDF to several, supporting single-page splitting, by page count, by copy count, and by range
* **Rotate PDF**: Rotate each page by 90°, 180°, and 270° clockwise
* **Extract Text**: Extract plain text from PDF files without formatting
* **Extract Images**: Extract images from PDF files and save them in original format
* **Images to PDF**: Convert images to one PDF
* **PDF to Images**: Convert each page to image
* **PDF to Long Image**: Convert each page to image and merge into a long image
* **Delete Pages**: Delete specified pages from a PDF file
* **Add Page Numbers**: Add page numbers to a PDF file with various formatting options
* **Edit Bookmark**: Edit the bookmark of PDF
* **Merge Invoices**: Merge multiple Chinese invoice PDFs into one for easy printing

## Running Method

**Important for Windows Users:** If you are upgrading from a version older than 1.0.0, please uninstall the previous version manually before installing this one to avoid potential conflicts.

There are two types of pre-compiled packages, installers and portable packages. [Download](https://github.com/chianjin/PDFeXpress/releases) and install or unzip it, run `PDFeXpress.exe`.

You can also download from: [Quark Cloud Drive](https://pan.quark.cn/s/c50973b1f9c8?pwd=5RTu)

## Build

If you want to build the application yourself, follow these steps:

### Prerequisites

This project supports internationalization and requires the xgettext tool to compile `.po` files.

On Windows, you need to download [GUN gettext](https://mlocati.github.io/articles/gettext-iconv-windows.html).

### Procedure

```shell
> git clone https://github.com/chianjin/PDFeXpress.git
> cd PDFeXpress
> pip install -r requirements-dev
> <Path to>\msgfmt src\locale\zh_CN\LC_MESSAGES\PDFeXpress.po
> python build.py
```

Precompiled package and installer are saved in the `release` directory.

**Note**: Installer will auto build on Windows, if [Inno Setup](https://jrsoftware.org/isinfo.php) installed.

## License

Copyright (c) 2025 chian.jin@gmail.com.

This project is licensed under the GNU Affero General Public License Version 3.
See the [LICENSE](LICENSE) file for full details.

## Third-Party Acknowledgements

This project utilizes several third-party libraries. The following is a list of these libraries and their respective licenses and homepages/source code.

| Library     | License                                                                                               | Homepage/Source                                                       |
| ----------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Python      | [Python Software Foundation License](https://docs.python.org/3/license.html)                          | [python.org](https://www.python.org/)                                 |
| PyMuPDF     | [GNU AGPLv3](https://www.gnu.org/licenses/agpl-3.0.en.html)                                           | [PyMuPdf - GitHub](https://github.com/pymupdf/PyMuPDF)                |
| Pillow      | [Pillow License (MIT-CMU)](https://github.com/python-pillow/Pillow/blob/main/LICENSE)                 | [python-pillow.org](https://python-pillow.org/)                       |
| tkinterdnd2 | [MIT License](https://github.com/Eliav2/tkinterdnd2/blob/master/LICENSE)                             | [pypi.org/project/tkinterdnd2](https://pypi.org/project/tkinterdnd2/) |
| PyInstaller | [GPL 2.0 with linking exception](https://github.com/pyinstaller/pyinstaller/blob/develop/LICENSE.txt) | [pyinstaller.org](https://pyinstaller.org/)                           |

The application is built using PyInstaller, which has a special license that allows for the distribution of bundled applications (including commercial ones) without being subject to the GPL.