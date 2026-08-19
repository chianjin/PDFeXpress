from collections import namedtuple

from util.i18n import gettext_text as _

feature = namedtuple('feature', ['feature_id', 'display_name', 'executive_text'])

FEATURE_LIST = (
    (
        ('document_assembly', _('Document Assembly')),
        (
            feature('merge_pdf', _('Merge PDF'), _('Merge')),
            feature('interleave_merge', _('Interleave Merge'), _('Merge')),
            feature('split_pdf', _('Split PDF'), _('Split')),
            feature('divide_pages', _('Divide Pages'), _('Divide')),
            feature('rotate_pdf', _('Rotate PDF'), _('Rotate')),
            feature('delete_pages', _('Delete Pages'), _('Delete')),
        ),
    ),
    (
        ('content_extraction', _('Content Extraction')),
        (
            feature('extract_text', _('Extract Text'), _('Extract')),
            feature('extract_images', _('Extract Images'), _('Extract')),
        ),
    ),
    (
        ('format_conversion', _('Format Conversion')),
        (
            feature('images_to_pdf', _('Images to PDF'), _('Convert')),
            feature('pdf_to_images', _('PDF to Images'), _('Convert')),
            feature('pdf_to_long_image', _('PDF to Long Image'), _('Convert')),
        ),
    ),
    (
        ('document_compression', _('Document Compression')),
        (
            feature('quick_compress', _('Quick Compress'), _('Compress')),
            feature('deep_compress', _('Deep Compress'), _('Compress')),
        ),
    ),
    (
        ('page_annotation', _('Page Annotation')),
        (
            feature('add_page_numbers', _('Add Page Numbers'), _('Add')),
            feature('add_watermark', _('Add Watermark'), _('Add')),
            feature('edit_bookmarks', _('Edit Bookmarks'), _('Edit')),
        ),
    ),
    (
        ('document_security', _('Document Security')),
        (
            feature('encrypt_pdf', _('Encrypt PDF'), _('Encrypt')),
            feature('decrypt_pdf', _('Decrypt PDF'), _('Decrypt')),
        ),
    ),
    (
        ('Invoice Processing', _('Invoice Processing')),
        (feature('merge_invoices', _('Merge Invoices'), _('Merge')),),
    ),
)
