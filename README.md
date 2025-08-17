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
For our purposes, we will 
```
{
  "@context": {
    "ccmm": "https://model.ccmm.cz/research-data/",
    "datacite": "https://model.ccmm.cz/vocabulary/datacite#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "dct": "http://purl.org/dc/terms/",
    "dcat": "http://www.w3.org/ns/dcat#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "adms": "http://www.w3.org/ns/adms#",
    "vcard": "http://www.w3.org/2006/vcard/ns#",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },

  "@id": "https://mk.gov.cz/evidence-knihoven-adresar-knihoven-evidovanych-ministerstvem-kultury-a-souvisejici-informace-cs-341",
  "@type": "ccmm:Dataset",

  "dct:title": { "cs": "Evidence knihoven evidovaných MK ČR" },

  "datacite:hasDescription": {
    "@id": "https://example.org/datasets/evidence-knihoven/description1",
    "@type": "ccmm:Description",
    "rdfs:label": "Seznam knihoven evidovaných Ministerstvem kultury ČR.",
    "dct:language": "cs",
    "dct:type": "abstract"
  },

  "ccmm:hasIdentifier": {
    "@id": "https://mk.gov.cz/evidence-knihoven-adresar-knihoven-evidovanych-ministerstvem-kultury-a-souvisejici-informace-cs-341",
    "@type": "ccmm:Identifier",
    "skos:notation": { "@value": "https://mk.gov.cz/evidence-knihoven-adresar-knihoven-evidovanych-ministerstvem-kultury-a-souvisejici-informace-cs-341", "@type": "xsd:anyURI" },
    "adms:schemeAgency": "Ministerstvo kultury ČR",
    "dct:created": { "@value": "2025-08-17", "@type": "xsd:date" }
  },

  "dct:publisher": {
    "@id": "https://mk.gov.cz/",
    "@type": "ccmm:Organization",
    "rdfs:label": "Ministerstvo kultury České republiky"
  },

  "dct:issued":   { "@value": "2025-08-17", "@type": "xsd:date" },
  "dct:modified": { "@value": "2025-08-17", "@type": "xsd:date" },

  "ccmm:hasPrimaryLanguage": {
    "@id": "http://id.loc.gov/vocabulary/iso639-1/cs",
    "rdfs:label": "čeština"
  },

  "ccmm:hasLocation": {
    "@id": "http://publications.europa.eu/resource/authority/country/CZE",
    "rdfs:label": "Czech Republic"
  },

  "ccmm:hasDistribution": [
    {
      "@id": "https://mk.gov.cz/evidence-knihoven/evidence.xlsx",
      "@type": "ccmm:Distribution",
      "dct:title": "Evidence knihoven – XLSX",
      "dct:format": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "dcat:mediaType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "dcat:accessURL": "https://mk.gov.cz/evidence-knihoven-adresar-knihoven-evidovanych-ministerstvem-kultury-a-souvisejici-informace-cs-341"
    }
  ],

  "ccmm:hasTermsOfUse": {
    "@id": "https://creativecommons.org/licenses/by/4.0/",
    "dct:title": "Creative Commons Attribution 4.0 International (CC BY 4.0)"
  },

  "dct:accrualPeriodicity": {
    "@id": "http://publications.europa.eu/resource/authority/frequency/IRREG",
    "rdfs:label": "Irregular"
  }
}

```

