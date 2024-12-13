# PDF eXpress

[[English]](https://github.com/chianjin/PDFeXpress/blob/main/README.md)  [[简体中文]](https://github.com/chianjin/PDFeXpress/blob/main/README.zh_CN.md)

**PDF eXpress**, an application used to operate PDF, wrote by using Python.

## Developing Environment

- Python 3.11
- PyMuPDF==1.22.5
- Pillow
- Nuitka==1.8.6

## Current Version

The current version is 0.4-BETA, tested on Windows 11 amd64.

## Main Functions

- **Merge**: Merge multiple PDF files into one PDF
- **Split**: Splits a PDF into multiple PDFs, supporting single page splitting, split by number of pages, by number of
  copies, and by range
- **Rotate** : Rotate each PDF page with 90°, 180°, and 270° clockwise
- **Extract Images**: Extracts the images contained in the PDF file and saves them in the original data format
- **Extract Text**: Extracts plain text contained in a PDF file, without formatting
- **PDF to Image** : Converts each entire pages of a PDF file to images
- **Image to PDF**: Converts images file to PDF
- **Merge Invoice**: Merges multiple Chinese invoices into one PDF

## Running Method

There are two type binary, installer and portable packages. [Download](https://github.com/chianjin/PDFeXpress/releases)
and install or unzip it, run `PDFeXpress.exe`.

Can also download from: [Baidu](https://pan.baidu.com/s/14I_0RdbfVqpWORXfgYlEjQ?pwd=i4xb)

## Build

If you want to build the application yourself. Please follow these steps below:

```shell
> git clone https://github.com/chianjin/PDFeXpress.git
> cd PDFeXpress
> pip install -r requirements
> python <Python Path>\Tools\i18n\msgfmt.py src\locale\zh_CN\LC_MESSAGES\PDFeXpress.po
> python build.py
```

The compiled binary package and installer are saved in `release` folder.

**Note**: The setup package will be created if Inno Setup 6.x is already installed on Windows.
