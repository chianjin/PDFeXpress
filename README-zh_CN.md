# PDF eXpress

[[English]](https://github.com/chianjin/PDFeXpress/blob/main/README.md)  [[简体中文]](https://github.com/chianjin/PDFeXpress/blob/main/README-zh_CN.md)

**PDF eXpress**是一款以 Python 编写的，用于 PDF 文件操作的应用程序。

## 开发环境

- Python 3.13
- PyMuPDF==1.26.5
- pillow==12.0.0
- tkinterdnd2==0.4.3
- pyinstaller==6.16.0

## 当前版本

当前版本为 1.0.0，已经在64位的Windows 11上测试通过。

## 主要功能

* **合并 PDF**：将多个 PDF 文件合并为一个 PDF
* **交叉合并**：将两个 PDF 文件交叉合并
* **拆分 PDF**：将 PDF 拆分为多个PDF，支持单页分割、按页数分割、按份数分割以及按范围分割
* **旋转 PDF**：将 PDF 页面顺时针旋转90°、180°和270°
* **提取文本**：提取 PDF 文件所包含的纯文本，不包含格式
* **提取图像**：提取 PDF 文件所包含的图像，按照原始数据格式保存
* **图像转PDF**：将图像文件转换为 PDF
* **PDF转图像**：将 PDF 文件页面转换为图像
* **PDF转长图**：将 PDF 转换成图像并拼合成长图
* **删除页面**：从 PDF 文件中删除指定页面
* **编辑书签**：编辑 PDF 的书签
* **合并发票**：合并多个 PDF 格式中国发票方便打印

## 运行方式

有两种形式的预编译包，安装包和绿色包，[下载](https://github.com/chianjin/PDFeXpress/releases) 、安装或解压，运行
`PDFeXpress.exe`。

也可以从这里下载：[夸克网盘](https://pan.quark.cn/s/c50973b1f9c8?pwd=5RTu)

## 构建

若打算自行构建可执行文件，按照以下步骤操作：

### 准备工作

本项目支持国际化，需要 xgettext 工具编译 `po`文件。

Windows平台上需要下载 [GUN gettext](https://mlocati.github.io/articles/gettext-iconv-windows.html) 。

### 操作流程

```shell
> git clone https://github.com/chianjin/PDFeXpress.git
> cd PDFeXpress
> pip install -r requirements-dev
> <Path to>\msgfmt src\locale\zh_CN\LC_MESSAGES\PDFeXpress.po
> python build.py
```

预编译包、安装程序保存在`release`目录中。

**注**：在 Windows 系统上，若安装了 [Inno Setup](https://jrsoftware.org/isinfo.php)，安装程序会自动构建。

## 版权和许可协议

Copyright (c) 2025 chian.jin@gmail.com.

本项目采用 GNU Affero General Public License Version 3 许可协议。
详情请参阅 [LICENSE](LICENSE) 文件。

## 第三方软件鸣谢

本项目使用了一些第三方库。以下是这些库及其各自的许可协议和主页/源代码。

| 库           | 许可协议                                                                                                  | 主页/源代码                                                                |
| ----------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Python      | [Python Software Foundation License](https://docs.python.org/3/license.html)                          | [python.org](https://www.python.org/)                                 |
| PyMuPDF     | [GNU AGPLv3](https://www.gnu.org/licenses/agpl-3.0.zh-cn.html)                                        | [PyMuPdf - GitHub](https://github.com/pymupdf/PyMuPDF)                |
| Pillow      | [Pillow License (MIT-CMU)](https://github.com/python-pillow/Pillow/blob/main/LICENSE)                 | [python-pillow.org](https://python-pillow.org/)                       |
| tkinterdnd2 | [MIT License](https://github.com/pmgagne/tkinterdnd2/blob/master/LICENSE)                             | [pypi.org/project/tkinterdnd2](https://pypi.org/project/tkinterdnd2/) |
| PyInstaller | [GPL 2.0 with linking exception](https://github.com/pyinstaller/pyinstaller/blob/develop/COPYING.txt) | [pyinstaller.org](https://pyinstaller.org/)                           |

本应用程序使用 PyInstaller 打包。该工具的许可协议包含特殊例外，允许分发捆绑后的应用程序（包括商业应用）而不受 GPL 的限制。