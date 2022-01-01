nuitka --show-progress --show-memory --standalone --onefile --mingw64 --windows-disable-console^
 --windows-icon-from-ico=src\PDFExpress.ico --include-data-file=src\PDFExpress.ico=.\PDFExpress.ico^
 --plugin-enable=tk-inter --plugin-enable=multiprocessing --output-dir=build src\PDFExpress.py

REM nuitka --show-progress --show-memory --standalone --mingw64^
REM --windows-icon-from-ico=src\PDFExpress.ico --include-data-file=src\PDFExpress.ico=.\PDFExpress.ico^
REM --plugin-enable=tk-inter --plugin-enable=multiprocessing --output-dir=build src\PDFExpress.py
