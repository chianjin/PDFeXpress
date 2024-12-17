# PDF Express

[[English]](https://github.com/chianjin/PDFeXpress/blob/main/README.md)  [[Simplified Chinese]](https://github.com/chianjin/PDFeXpress/blob/main/README.zh_CN.md)

**PDF Express** is a Python-based application for PDF file operations.

## Development Environment

- Python 3.11
- PyMuPDF==1.22.5
- Pillow
- Nuitka==1.8.6

## Current Version

The current version is 0.4.1-BETA, which has been tested on 64-bit Windows 11.

## Main Functions

* **Merge PDF**：Merge multiple PDF files into one
* **Split PDF**：Split one PDF to serval, supporting single-page splitting, by page count, by copy count, and by range
* **Rotate PDF**：Rotate each page by 90°, 180°, and 270° clockwise
* **Extract Text**：Extract plain text from PDF files without formatting
* **Extract Images**：Extract images from PDF files and save them in original format
* **Image to PDF**：Convert images to one PDF
* **PDF to Image**：Convert each page to image
* **PDF to Long Image**：Convert each page to image and merge into a long image
* **Merge Invoice**：Merge multiple Chinese invoice PDFs into one for easy printing

## Running Method

There are two types of pre-compiled packages, installers and portable
packages. [Download](https://github.com/chianjin/PDFeXpress/releases) and install or unzip it, run `PDFeXpress.exe`.

You can also download from: [Baidu](https://pan.baidu.com/s/14I_0RdbfVqpWORXfgYlEjQ?pwd=i4xb)

## Build

If you want to build the application yourself, follow these steps:

```shell
> git clone https://github.com/chianjin/PDFeXpress.git
> cd PDFeXpress
> pip install -r requirements
> python <Python Path>\Tools\i18n\msgfmt.py src\locale\zh_CN\LC_MESSAGES\PDFeXpress.po
> python build.py
```

Precompiled package and installer are saved in the `release` directory.

**Note**: Installer will auto build on Windows, if [Inno Setup](https://jrsoftware.org/isinfo.php) installed.