## Automatic Data Parcing of libraries database
This section is dedicated to Data Parcing Process implemented in Python. The data parcing from HTML page was made using library **BeautifulSoup**. The script  ```Retrieval.py``` extracts the URL for the .xlsx file and then downloads it. This way, we don't need a fixed file name, which changes with the date when the new dataset is uploaded. The file is being saved with a date stamp (e.g., library-records_2025-08-06.xlsx) and also as latest (library-records_latest.xlsx). The SHA-256 hash is used to verify file integrity, detect changes, and safely archive only new versions without storing duplicates.
#### Automatization of the script
For our purposes, we used GitHub Actions to schedule and execute the process. We arbitrary chose to execute the script each Wednesday at 13:00. In a real-world local deployment scenario, this could alternatively be handled using **Windows Task Scheduler** on Windows or **cron** on Linux.
##  Data preprocessing
The data transformation was done in the next way:
  1. Changing some of the most import columns to snake_case style for pottential simplifying the SQL workflow (Easily could be applied on all columns, but for our purposes we did it for the most crucial columns only)
  2. Making **Evidencni_cislo** column an index column, so it can be used as a primary key in SQL database (we also verified that there is no duplicates in the latest version of dataset)
  3. Adding zeroes to the beginning of **ICO** values in **ico_provozovatele** column (if needed). Now old business registration numbers satisfy the new rules (business registration numbers must have 8 digits)
  4. Whitespace normalization + lowercase transformation of emails
  5. Removing of nonsense in **knihovna_web** column
  6. Making ASCII columns from the most important string columns to provide names without diacritics.
  7. Normalising **knihovna_psc** on 5 digits
  8. The dates are transformed on **datetime** according to ISO 8601 standard.
  9. Exporting dataframe as CSV file with UTF-8 encoding.
The cleaning script is provided as ```Cleaning.py```. The cleaned dataset is library-records_clean.py

## Data Storage and Security
To ensure permanent and secure storage of the downloaded data, we would use a central repository with regular backups, such as a database (PostgreSQL, MySQL) or a file system on a secured server. Access would be restricted to authorized users through authentication and encryption
```
           ┌────────────────────┐       
           │   Scheduler/Trigger│
           │(cron/WTS/GitHubAct.)│        
           └─────────┬──────────┘
                     │                              
                     ▼                              
          ┌──────────────────────┐                  
          │ Data Retrieval Script│
          │       (Python)       │
          └─────────┬────────────┘
                    │  SFTP (SSH)  ←— secure transfer (auth + encryption)
                    ▼
        ┌──────────────────────────┐
        │   Secure Storage (Prod)  │
        │  - PostgreSQL (TDE/KMS)  │
        │  - Encrypted filesystem  │
        └──────────┬───────────────┘
                   │
                   ▼
       ┌─────────────────────────────┐
       │ Backups & Versioning        │  (3-2-1, offsite, immutability)
       │ + periodic restore testing  │
       └──────────┬──────────────────┘
                  │
                  ▼
        ┌──────────────────────────┐
        │ Observability & Audits   │
        │ (logs, metrics, alerts,  │
        │  provenance)             │
        └──────────────────────────┘
```

## Describing dataset using Czech Core Metadata Model
The Czech Core Metadata Model (CCMM) is a national metadata model for describing datasets, based on the European DCAT-AP standard. In practice, it is implemented through the so-called DCAT-AP-CZ application profile – an open formal standard for open data catalogues in the Czech Republic. The official documentation of DCAT-AP-CZ is available on the Open Data Portal (ofn.gov.cz) and describes all properties required in the NKOD (Národním katalogu otevřených dat, National Open Data Catalogue).
For our purposes, we can use the schema provided here: https://www.muni.cz/en/research/publications/2489659. 
```
{
  "id": "library-records-clear",
  "language": "cs",
  "date_created": "2025-08-17",
  "date_updated": "2025-08-17",
  "patron": {
    "given_name": "Petr",
    "family_name": "Novak",
    "email": ["petr_novak@example.com"]
  },
  "data_provider": {
    "organisation": {
      "name": "Ministerstvo kultury České republiky",
      "address": "Maltézské náměstí 471/1, Praha 1",
      "url": "https://mk.gov.cz",
      "organisation_category": "Government",
      "contact_person": {
        "given_name": "Jan",
        "family_name": "Novák",
        "email": ["info@mkcr.cz"]
      }
    }
  },
  "data_specification": {
    "title": "Evidence knihoven – registrované knihovny v ČR",
    "identifier": "urn:muni:library-records:2025",
    "description": "Dataset of libraries registered with the Ministry of Culture of the Czech Republic. Cleaned and standartised version for research project.",
    "version": "1.0",
    "subject": ["Libraries", "Public institutions", "Czech Republic"],
    "statements": {
      "terms_of_use": "Dataset is publicly available for research purposes.",
      "data_licence": "CC-BY 4.0",
      "provenance": "Official registry from Ministry of Culture ČR"
    },
    "data_categories": {
      "data_structure": "Tabular",
      "data_sensitivity": "Public Data",
      "data_updates": "Periodically updated"
    },
    "distribution": {
      "data_format": "CSV",
      "access_instructions": "Dataset can be accessed via the Ministry of Culture webpage or project repository.",
      "access_url": "https://mk.gov.cz/evidence-knihoven-adresar-knihoven-evidovanych-ministerstvem-kultury-a-souvisejici-informace-cs-341",
      "download_url": "TODO"
    }
  }
}
```


