# 基础类型 (不参与分组，直接保留字典格式)
BASE_FILETYPES = {
    'ALL': [('所有文件', '*.*')],
    'CSV': [('CSV 数据文件', '*.csv')],
}

# ==========================================
# 自动发现区 (格式规范: 变量名以 _GROUP 结尾)
# 结构: (组前缀, 聚合描述, 详细格式字典)
# ==========================================

IMAGE_GROUP = (
    'IMAGE',
    '图像文件',
    {
        'JPEG': ('JPEG 图像文件', ('*.jpg', '*.jpeg')),
        'PNG': ('PNG 图像文件', '*.png'),
        'WEBP': ('WebP 图像文件', '*.webp'),
        'BMP': ('BMP 图像文件', '*.bmp'),
        'TIFF': ('TIFF 图像文件', ('*.tif', '*.tiff')),
        'GIF': ('GIF 图像文件', '*.gif'),
    },
)

PYMUPDF_GROUP = (
    'MUPDF_DOC',
    'PyMuPDF 支持的文档',
    {
        'PDF': ('PDF 文档', '*.pdf'),
        'EPUB': ('EPUB 电子书', '*.epub'),
        'XPS': ('XPS 文档', ('*.xps', '*.oxps')),
        'CBZ': ('CBZ 漫画归档', '*.cbz'),
        'FB2': ('FB2 电子书', '*.fb2'),
        'SVG': ('SVG 矢量图', '*.svg'),
    },
)
