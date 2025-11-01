# PDF eXpress

[[English]](https://github.com/chianjin/PDFeXpress/blob/main/README.md)  [[简体中文]](https://github.com/chianjin/PDFeXpress/blob/main/README.zh_CN.md)

**PDF eXpress**是一款以 Python 编写的，用于 PDF 文件操作的应用程序。

## 开发环境

- Python 3.13
- PyMuPDF==1.26.4
- pillow==11.3.0
- tkinterdnd2==0.4.3
- pyinstaller==6.16.0

## 当前版本

当前版本为 0.4.2-BETA，已经在64位的Windows 11上测试通过。

## 主要功能

* **合并 PDF**：将多个 PDF 文件合并为一个 PDF
* **拆分 PDF**：将 PDF 拆分为多个PDF，支持单页分割、按页数分割、按份数分割以及按范围分割
* **旋转 PDF**：将 PDF 页面顺时针旋转90°、180°和270°
* **编辑 TOC**：编辑 PDF 的目录
* **提取文本**：提取 PDF 文件所包含的纯文本，不包含格式
* **提取图像**：提取 PDF 文件所包含的图像，按照原始数据格式保存
* **图像转PDF**：将图像文件转换为 PDF
* **PDF转图像**：将 PDF 文件页面转换为图像
* **PDF转长图**：将 PDF 转换成图像并拼合成长图
* **合并发票**：合并多个 PDF 格式中国发票方便打印

## 运行方式

有两种形式的预编译包，安装包和绿色包，[下载](https://github.com/chianjin/PDFeXpress/releases) 、安装或解压，运行
`PDFeXpress.exe`。

也可以从这里下载：[百度网盘](https://pan.baidu.com/s/14I_0RdbfVqpWORXfgYlEjQ?pwd=i4xb)

## 构建

若打算自行构建可执行文件，按照以下步骤操作：

```shell
> git clone https://github.com/chianjin/PDFeXpress.git
> cd PDFeXpress
> pip install -r requirements
> python <Python Path>\Tools\i18n\msgfmt.py src\locale\zh_CN\LC_MESSAGES\PDFeXpress.po
> python build.py
```

预编译包、安装程序保存在`release`目录中。

**注**：在 Windows 系统上，若安装了 [Inno Setup](https://jrsoftware.org/isinfo.php)，安装程序会自动构建。
