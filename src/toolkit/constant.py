from toolkit.i18n import gettext_text as _

FILE_TYPES_ALL = [(_('All Files'), '*.*')]

FILE_TYPES_PDF = [(_('PDF Files'), '*.pdf')]

FILE_TYPES_CSV = [(_('CSV Files'), '*.csv')]

FILE_TYPES_IMAGE = [
    (
        _('Image Files'),
        ('*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp', '*.tif', '*.tiff', '*.gif'),
    )
]
FILE_TYPES_JPEG = [(_('JPEG Files'), ('*.jpg', '*.jpeg'))]
FILE_TYPES_PNG = [(_('PNG Files'), '*.png')]
FILE_TYPES_WEBP = [(_('WebP Files'), '*.webp')]
FILE_TYPES_BMP = [(_('BMP Files'), '*.bmp')]
FILE_TYPES_TIFF = [(_('TIFF Files'), ('*.tif', '*.tiff'))]

FILE_TYPES_GIF = [(_('GIF Files'), '*.gif')]

FILE_TYPES_IMAGES = [
    FILE_TYPES_IMAGE[0],
    FILE_TYPES_JPEG[0],
    FILE_TYPES_PNG[0],
    FILE_TYPES_WEBP[0],
    FILE_TYPES_BMP[0],
    FILE_TYPES_TIFF[0],
    FILE_TYPES_GIF[0],
]

HELP_ICON = 'data/help24.png'
