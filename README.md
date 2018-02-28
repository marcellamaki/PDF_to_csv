How to use PDF to CSV converter

Currrently subscribers.csv is an empty file.

To run with the current TestReport (which has been added to the repo PDFParser as TestReport.pdf), run python PDFparser.py from the command line.

The script will parse the PDF and convert it into a json object, and then parse that json object and save it to subscribers.csv.

For ease of reading the csv, incidents of missing data have been labeled "none". This could easily be converted to an empty string.
