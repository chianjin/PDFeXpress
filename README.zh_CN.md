# PDF eXpress

[[English]](https://github.com/chianjin/PDFeXpress/blob/main/README.md)  [[简体中文]](https://github.com/chianjin/PDFeXpress/blob/main/README.zh_CN.md)

**PDF eXpress**是一款以Python编写的，用于PDF文件操作的应用程序。

## 开发环境

- Python 3.10.1
- Nuitka==0.6.19.1
- Pillow==9.0.0
- psutil==5.9.0
- PyMuPDF==1.19.4

## 当前版本

当前版本为 0.1.1-BETA，已经在64位的Windows 10和11上测试通过。未来计划测试Linux、FreeBSD系统。

## 主要功能

* **合并**：将多个PDF文件合并为一个PDF
* **分割**：将PDF分割为多个PDF，支持单页分割、按页数分割、按份数分割以及按范围分割
* **旋转**：将PDF页面顺时针、逆时针旋转90°，以及旋转180°
* **压缩**：通过压缩页面所包含的图像，减小PDF文件大小
* **提取图像**：提取PDF文件所包含的图像，按照原始数据格式保存
* **提取文本**：提取PDF文件所包含的纯文本，不包含格式
* **PDF转换为图像**：把PDF文件整个页面转换为图像
* **图像转换为PDF**：把图像文件转换为PDF

## 运行方式

下载已经编译好的安装程序，运行安装即可。

阿里云盘：[PDFeXpress-0.1BETA-setup-x64.exe](https://www.aliyundrive.com/s/6sqqjkPFxKc)

## 构建

如果你打算自行构建可执行文件，按照以下步骤操作：

```shell
> git clone https://github.com/chianjin/PDFeXpress.git
> cd PDFeXpress
> pip install -r requirements
> python <Python Path>\Tools\i18n\msgfmt.py locale\zh_CN\LC_MESSAGES\PDFeXpress.po
> nuitka-build.cmd
```

编译后的可执行文件，保存在`build\PDFeXpress.dist`目录中，运行 `PDFeXpress.exe`.

另外，也可以下载安装**Inno Setup**，打开`PDFeXpress.iss`，构建安装程序。
