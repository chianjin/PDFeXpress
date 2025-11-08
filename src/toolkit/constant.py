# toolkit/constant.py

from toolkit.i18n import gettext_text as _

FILE_TYPES_ALL = [(_("All Files"), "*.*")]

FILE_TYPES_PDF = [(_("PDF Files"), "*.pdf")]

FILE_TYPES_CSV = [(_("CSV Files"), "*.csv")]

FILE_TYPES_IMAGE = [
    (
        _("Image Files"),
        ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.bmp", "*.tif", "*.tiff", "*.gif"),
    )
]
FILE_TYPES_JPEG = [(_("JPEG Files"), ("*.jpg", "*.jpeg"))]
FILE_TYPES_PNG = [(_("PNG Files"), "*.png")]
FILE_TYPES_WEBP = [(_("WebP Files"), "*.webp")]
FILE_TYPES_BMP = [(_("BMP Files"), "*.bmp")]
FILE_TYPES_TIFF = [(_("TIFF Files"), ("*.tif", "*.tiff"))]

FILE_TYPES_GIF = [(_("GIF Files"), "*.gif")]

FILE_TYPES_IMAGES = [
    FILE_TYPES_IMAGE[0],
    FILE_TYPES_JPEG[0],
    FILE_TYPES_PNG[0],
    FILE_TYPES_WEBP[0],
    FILE_TYPES_BMP[0],
    FILE_TYPES_TIFF[0],
    FILE_TYPES_GIF[0],
]

HELP_ICON = "data/help24.png"

RANGE_SYNTAX_HELP = _(
"""自定义页面范围语法说明：

基本语法：
- 逗号分隔：1,3,5 表示第1页、第3页、第5页
- 连字符范围：3-7 表示第3到第7页（包含两端）
- 省略范围：-10 表示从首页到第10页，5- 表示从第5页到最后
- 步长语法：1-10:2 表示从第1到第10页，每隔2页取一页（1,3,5,7,9）
- 全局步长：:3 表示从首页到最后页，每隔3页取一页

组合使用：
- 混合表达：1,3-5,7-:2 表示第1页，第3-5页，第7页到最后页每隔2页取一页

多组范围：
- 分号分隔：1,3,6-9;4-6,8;1-5 表示3个不同的范围组，将生成3个PDF文件

重复与反向：
- 允许重复：+ 号前缀表示允许重复页（如 +4-8,6,9-12）
- 反向范围：在 + 模式下支持反向（如 +9-5 表示第9页到第5页的反向）

注意事项：
- 默认模式下自动去重
- 不在 + 模式下使用反向范围会报错
- 所有页码以1开始计数
"""
)
