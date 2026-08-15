"""Delete pages worker.

Deletes pages specified by a page-range expression from a single input PDF and
writes the result into an output folder. The expression uses the same syntax
as split_pdf's custom-range mode (see ``util.page_range_parser``) but each
';' group is treated as a SET OF PAGES TO DELETE, producing one output PDF
per group.

This is the complement of split_pdf's custom-range mode:
  split   -> keep the specified pages, one file per ';' group
  delete  -> delete the specified pages, one file per ';' group

Enhanced mode (+) is intentionally NOT supported for this feature.

Single-file, in-memory operation -- no subprocess or progress dialog. The
frame calls ``delete_pages`` synchronously and handles UI feedback.
"""

from pathlib import Path

import pymupdf

from util.i18n import gettext_text as _


def delete_pages(params: dict) -> str:
    """Delete pages per group and write results into the output folder.

    Returns a summary string (possibly listing per-file failures). Raises
    ValueError when the range expression matches no pages or no output is
    written. Any other runtime failure (unreadable file, save error)
    propagates to the caller.

    Frame-side validation already guarantees a non-empty, non-'+' expression
    and an existing input file, so this function trusts those inputs.
    """
    inputs = params['inputs']
    output = params['output']
    options = params['options']

    src = Path(inputs[0])
    groups = options['groups']
    raw_groups = options['raw_groups']

    doc = pymupdf.open(str(src))
    try:
        total = options['total_pages']

        out_dir = Path(output)
        out_dir.mkdir(parents=True, exist_ok=True)

        total_outputs = len(groups)
        failures = []
        produced = 0

        for idx, del_pages in enumerate(groups, start=1):
            gexpr = raw_groups[idx - 1] if raw_groups else ''
            name = f'{src.stem}.D{gexpr.replace(":", "S")}.pdf'
            try:
                del_set = set(del_pages)
                out_doc = pymupdf.open()
                try:
                    for p in range(total):
                        if p not in del_set:
                            out_doc.insert_pdf(doc, from_page=p, to_page=p)
                    out_doc.save(str(out_dir / name))
                finally:
                    out_doc.close()
                produced += 1
            except Exception as exc:
                failures.append((name, f'{type(exc).__name__}: {exc}'))

        if produced == 0:
            raise ValueError(_('No output files were written.'))

        summary = _('Delete Pages') + f' ({produced}/{total_outputs})'
        if failures:
            summary += (
                '\n' + _('Failed:') + ' ' + '; '.join(f'{n}: {e}' for n, e in failures)
            )
        return summary
    finally:
        doc.close()
