from collections import defaultdict, namedtuple

function = namedtuple('Function', ['display_name', 'execute_text', 'row', 'column'])

FUNCTION_LIST = defaultdict(lambda: function('尚未实现', '执行', -1, -1))
FUNCTION_LIST.update(
    {
        # 功能标识符: (显示名称, 执行按钮文本 ,行, 列)
        'merge_pdf': function('合并 PDF', '合并', 0, 0),
        'interleave_merge': function('交错合并', '合并', 0, 1),
        'split_pdf': function('拆分 PDF', '拆分', 0, 2),
        'rotate_pdf': function('旋转 PDF', '旋转', 0, 3),
        'extract_text': function('提取文本', '提取', 0, 4),
        'extract_images': function('提取图像', '提取', 0, 5),
        'images_to_pdf': function('图像转 PDF', '转换', 1, 0),
        'pdf_to_images': function('PDF 转图像', '转换', 1, 1),
        'pdf_to_long_image': function('PDF 转长图', '转换', 1, 2),
        'crypt_pdf': function('加密解密', '执行', 1, 3),
        'compress_pdf': function('压缩 PDF', '压缩', 1, 4),
        'delete_pages': function('删除页面', '删除', 1, 5),
        'add_page_numbers': function('添加页码', '添加', 2, 0),
        'add_watermark': function('添加水印', '添加', 2, 1),
        'edit_bookmarks': function('编辑书签', '编辑', 2, 2),
        'merge_invoices': function('合并发票', '合并', 2, 3),
        'files_to_pdf': function('文件转 PDF', '转换', 2, 4),
        'pdf_to_docx': function('PDF 转 DOCX', '转换', 2, 5),
    }
)

