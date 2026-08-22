# PDF eXpress

[[English]](https://github.com/chianjin/PDFeXpress/blob/main/README.md)  [[简体中文]](https://github.com/chianjin/PDFeXpress/blob/main/README.zh_CN.md)

**PDF eXpress**是一款以 Python 编写的，用于 PDF 文件操作的应用程序。

## 开发环境

- Python 3.14
- pymupdf==1.28.2
- pillow==12.3.0
- tkinterdnd2==0.6.2
- pyinstaller==6.22.1

> **注意**：`setup_remotes.py` 仅用于本仓库，用于把改动同时推送到 Gitee 与 GitHub（双 push 地址）。**Fork 仓库请勿运行此脚本**，否则推送地址会被指向本项目的远端仓库。

## 当前版本

当前版本为 2.0，已经在 Windows 11 AMD64 和 Ubuntu 25.10 x86_64 系统上测试通过。

## 主要功能

**文档组装**

* **合并 PDF**：将多个 PDF 文件合并为一个 PDF
* **交叉合并**：将两个 PDF 文件交叉合并
* **拆分 PDF**：将 PDF 拆分为多个PDF，支持单页分割、按页数分割、按份数分割以及按自定义范围分割
* **分割页面**：将 PDF 页面按方向（纵向/横向）与份数分割为多个页面
* **旋转 PDF**：将 PDF 页面顺时针旋转90°、180°和270°
* **删除页面**：从 PDF 文件中删除指定页面

**内容提取**

* **提取文本**：提取 PDF 文件所包含的纯文本，不包含格式
* **提取图像**：提取 PDF 文件所包含的图像，按照原始数据格式保存

**格式转换**

* **图像转PDF**：将多个图像文件转换为 PDF
* **PDF转图像**：将 PDF 文件的每页转换为图像
* **PDF转长图**：将 PDF 转换成图像并拼合成长图

**文档压缩**

* **快速压缩**：批量压缩，使用内建清理管线
* **深度压缩**：逐页压缩并重新编码内嵌图像，压缩率更高

**页面标注**

* **添加页码**：为 PDF 文件添加页码，支持多种格式
* **添加水印**：为 PDF 页面添加水印
* **编辑书签**：编辑 PDF 的书签

**文档安全**

* **加密 PDF**：使用用户/所有者密码加密 PDF
* **解密 PDF**：移除 PDF 的密码保护

**发票处理**

* **合并发票**：合并多个 PDF 格式的中国发票方便打印

## 运行方式

**Windows 用户请注意：** 如果您是从 `1.0.0` 之前的旧版本升级，请务必先手动卸载旧版本，再安装新版本，以避免潜在的冲突。

有两种形式的预编译包，安装包和绿色包，[下载](https://github.com/chianjin/PDFeXpress/releases) 、安装或解压，运行
`PDFeXpress.exe`。

也可以从这里下载：[夸克网盘](https://pan.quark.cn/s/abc772612ee5?pwd=97sh)  [百度网盘](https://pan.baidu.com/s/14I_0RdbfVqpWORXfgYlEjQ?pwd=i4xb)

## 构建

若打算自行构建可执行文件，按照以下步骤操作：

### 准备工作

本项目支持国际化，翻译目录由 [Babel](https://babel.pocoo.org/)（位于 `requirements-dev`）管理，`i18n.py` 脚本封装了 pybabel 命令（`-e` 抽取 / `-u` 更新 / `-c` 编译 / `-a` 全部），构建步骤会把 `.po` 编译为 `.mo`。

### 操作流程

```shell
> git clone https://github.com/chianjin/PDFeXpress.git
> cd PDFeXpress
> pip install -r requirements-dev
> python i18n.py -c
> python build.py
```

> 注意：`python i18n.py -c`（即 `pybabel compile`）会跳过头部带 `#, fuzzy` 标记的目录。若中文目录未被编译，请先移除 `src/locale/zh_CN/LC_MESSAGES/pdfexpress.po` 头部的该标记。

预编译包、安装程序保存在`release`目录中。

**注**：在 Windows 系统上，若安装了 [Inno Setup](https://jrsoftware.org/isinfo.php)，安装程序会自动构建。

## 版权和许可协议

Copyright (c) 2026 chian.jin@gmail.com.

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
| PyInstaller | [GPL 2.0 with linking exception](https://github.com/pyinstaller/pyinstaller/blob/develop/LICENSE.txt) | [pyinstaller.org](https://pyinstaller.org/)                           |

本应用程序使用 PyInstaller 打包。该工具的许可协议包含特殊例外，允许分发捆绑后的应用程序（包括商业应用）而不受 GPL 的限制。