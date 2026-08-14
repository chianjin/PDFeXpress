"""Decrypt PDF worker.

A single encrypted PDF is opened, authenticated with the supplied password,
and re-saved without encryption (AES-256 -> plain). If the password is wrong
or missing, the operation fails with a clear message.

Single-file, instantaneous operation -- no subprocess or progress dialog.
The frame calls ``decrypt`` synchronously and handles UI feedback.
"""

from pathlib import Path

import pymupdf

from util.i18n import gettext_text as _


def decrypt(params: dict) -> None:
    """Decrypt the single input PDF and write the plain result.

    Raises ValueError when the password is wrong or missing. Any other
    runtime failure (unreadable file, save error) propagates to the caller.
    """
    inputs = params['inputs']
    output = params['output']
    password = params['options']['password']

    src = Path(inputs[0])
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(str(src))
    try:
        if doc.is_encrypted and doc.authenticate(password) == 0:
            raise ValueError(_('Wrong password or password required.'))
        doc.save(str(out_path))
    finally:
        doc.close()
