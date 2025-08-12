# Data Specialist Entry Task
This project was made as an author's implementation of tasks from entry test for Data Specialist position at MUNI ECON.
## Automatic Data Parcing of libraries database
This section is dedicated to Data Parcing Process implemented in Python. The data parcing from HTML page was made using standard libraries such as **BeautifulSoup**. The script extracts the URL for .xlsx from it and then download it. This way, we don't need a fixed file name, which changes with the date when the new dataset is uploaded. The file is being saved with a date stamp (e.g., library-records_2025-08-06.xlsx) and also as latest (copy library-records_latest.xlsx). The SHA-256 hash is used to verify file integrity, detect changes, and safely archive only new versions without storing duplicates.
##

##

##
