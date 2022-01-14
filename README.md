# PDF eXpress
[[English]](https://github.com/chianjin/PDFeXpress/blob/main/README.md)  [[简体中文]](https://github.com/chianjin/PDFeXpress/blob/main/README.zh_CN.md)

**PDF eXpress**,  an application used to operate PDF, wrote by using Python.

## Developing Environment

- Python 3.10.1
- Nuitka==0.6.19.1
- Pillow==9.0.0
- psutil==5.9.0
- PyMuPDF==1.19.4

## Current Version

The current version is 0.1.1-BETA, tested on Windows 10 and 11. Planing to test on Linux/FreeBSD.

## Main Functions

- **Merge**: Merge multiple PDF files into one PDF
- **Split**: Splits a PDF into multiple PDFs, supporting single page splitting, split by number of pages, by number of copies, and by range
- **Rotate** : Rotate each PDF page with 90° clockwise, counterclockwise, and 180°
- **Compression**: Reduces PDF file size by compressing the images contained in the page
- **Extract Images**: Extracts the images contained in the PDF file and saves them in the original data format
- **Extract Text**: Extracts plain text contained in a PDF file, without formatting
- **PDF to Image** : Converts the each entire pages of a PDF file to images
- **Image to PDF**: Converts images file to PDF

## Running Method

[Download](https://www.aliyundrive.com/s/6sqqjkPFxKc) the compiled binary installer and install and run PDFeXpress.exe or click the shortcut on your system.

AliyunDrive: [PDFeXpress-0.1BETA-setup-x64.exe](https://www.aliyundrive.com/s/6sqqjkPFxKc)

## Build

If you want to build the application yourself. Please follow these steps below:

```shell
> git clone https://github.com/chianjin/PDFeXpress.git
> cd PDFeXpress
> pip install -r requirements
> python <Python Path>\Tools\i18n\msgfmt.py locale\zh_CN\LC_MESSAGES\PDFeXpress.po
> nuitka-build.cmd
```

The compiled binary files are saved in `build\PDFeXpress.dist`, run `PDFeXpress.exe`.

Additionally, you may download and install **Inno Setup** , open the `PDFeXpress.iss` to build the installer.
