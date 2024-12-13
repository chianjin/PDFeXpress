# PDF eXpress

[[English]](https://github.com/chianjin/PDFeXpress/blob/main/README.md)  [[简体中文]](https://github.com/chianjin/PDFeXpress/blob/main/README.zh_CN.md)

**PDF eXpress**是一款以Python编写的，用于PDF文件操作的应用程序。

## 开发环境

- Python 3.11
- PyMuPDF==1.22.5
- Pillow
- Nuitka==1.8.6

## 当前版本

当前版本为 0.4-BETA，已经在64位的Windows 11上测试通过。

## 主要功能

* **合并**：将多个PDF文件合并为一个PDF
* **拆分**：将PDF拆分为多个PDF，支持单页分割、按页数分割、按份数分割以及按范围分割
* **旋转**：将PDF页面顺时针旋转90°、180°和270°
* **提取图像**：提取PDF文件所包含的图像，按照原始数据格式保存
* **提取文本**：提取PDF文件所包含的纯文本，不包含格式
* **PDF转换为图像**：把PDF文件整个页面转换为图像
* **图像转换为PDF**：把图像文件转换为PDF
* **合并发票**：合并多个中文发票

## 运行方式

有两种形式的预编译包，安装包和绿色包，[下载](https://github.com/chianjin/PDFeXpress/releases) 、安装或解压，运行`PDFeXpress.exe`。

也可以从这里下载：[百度网盘](https://pan.baidu.com/s/14I_0RdbfVqpWORXfgYlEjQ?pwd=i4xb)

## 构建

如果你打算自行构建可执行文件，按照以下步骤操作：

```shell
> git clone https://github.com/chianjin/PDFeXpress.git
> cd PDFeXpress
> pip install -r requirements
> python <Python Path>\Tools\i18n\msgfmt.py src\locale\zh_CN\LC_MESSAGES\PDFeXpress.po
> python build.py
```

预编译包安装程序保存在`release`目录中。

**注**：Windows 系统构建时，如果安装了 Inno Setup 6.x 的，将自动构建安装程序。
