This project was made as an author's implementation of the task he recently got to do.
## Automatic Data Parcing of libraries database
This section is dedicated to Data Parcing Process implemented in Python. The data parcing from HTML page was made using library **BeautifulSoup**. The script extracts the URL for the .xlsx file and then downloads it. This way, we don't need a fixed file name, which changes with the date when the new dataset is uploaded. The file is being saved with a date stamp (e.g., library-records_2025-08-06.xlsx) and also as latest (library-records_latest.xlsx). The SHA-256 hash is used to verify file integrity, detect changes, and safely archive only new versions without storing duplicates.
#### Automatization of the script
... to be continued ...
##  Data preprocessing
The data transformation was done in the next way:
  1. Changing some of the most import columns to snake_case style for pottential simplifying the SQL workflow  (Easily could be applied on all columns, but for our purposes we did it for the most crucial columns only)
  2. Making **Evidencni_cislo** column an index column, so it can be used as a primary key in SQL database (we also verified that there is no duplicates in the latest version of dataset)
  3. Adding zeroes to the beginning of **ICO** values in **ico_provozovatele** column (if needed). Now old business registration numbers satisfy the new rules (business registration numbers must have 8 digits)
  4. Whitespace normalization + lowercase transformation of emails
  5. Removing of nonsense in **knihovna_web** column
  6. Making ASCII columns from the most important string columns to provide names without diacritics.
  7. Normalising **knihovna_psc** on 5 digits
  8. The dates are transformed on **datetime** according to ISO 8601 standard.
  9. Exporting dataframe as CSV file with UTF-8 encoding.
     

##

##
