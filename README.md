## Automatic Data Parcing of libraries database
This section is dedicated to Data Parcing Process implemented in Python. The data parcing from HTML page was made using library **BeautifulSoup**. The script extracts the URL for the .xlsx file and then downloads it. This way, we don't need a fixed file name, which changes with the date when the new dataset is uploaded. The file is being saved with a date stamp (e.g., library-records_2025-08-06.xlsx) and also as latest (library-records_latest.xlsx). The SHA-256 hash is used to verify file integrity, detect changes, and safely archive only new versions without storing duplicates.
#### Automatization of the script
For our purposes, we used GitHub Actions to schedule and execute the process. We arbitrary chose to execute the script each Wednesday at 13:00. In a real-world local deployment scenario, this could alternatively be handled using **Windows Task Scheduler** on Windows or **cron** on Linux.
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

## Describing dataset usig CCMM
#### JSON for source
Below you can see how the JSON description of the source of the data can look. The used metadata schema can be found here: https://www.muni.cz/en/research/publications/2489659
JSON validates against the schema. (https://www.jsonschemavalidator.net/)
```
{
  "id": "https://example.org/meta/evidence-knihoven",
  "language": "ces",
  "date_created": "2025-08-15",
  "date_updated": "2025-08-15",

  "patron": {
    "given_name": "Bob",
    "family_name": "Novák",
    "email": ["bob.novak@example.org"]
  },

  "data_provider": {
    "organisation": {
      "name": "Ministerstvo kultury České republiky",
      "url": "https://mk.gov.cz",
      "organisation_category": "Government",
      "contact_person": {
        "given_name": "Alice",
        "family_name": "Novakova",
        "email": ["alice.novakova@example.org"]
      }
    }
  },

  "data_specification": {
    "title": "Evidence knihoven – adresář knihoven evidovaných MK ČR",
    "identifier": "https://mk.gov.cz/evidence-knihoven-adresar-knihoven-evidovanych-ministerstvem-kultury-a-souvisejici-informace-cs-341",
    "description": "Oficiální adresář veřejných a dalších knihoven evidovaných Ministerstvem kultury ČR včetně souvisejících informací.",
    "version": "1.0",
    "subject": ["knihovny", "evidence knihoven", "Česko"],
    "statements": {
      "terms_of_use": "Použití dat se řídí podmínkami zveřejněnými na webu MK ČR.",
      "data_licence": "Neudáno",
      "expenses": "0 CZK",
      "provenance": "Staženo z oficiální stránky MK ČR."
    },
    "data_categories": {
      "data_structure": "Tabular",
      "data_sensitivity": "Public Data",
      "data_updates": "Periodically updated",
      "date_embargo": ""
    },
    "distribution": {
      "data_format": "text/csv",
      "access_instructions": "Aktuální soubor hledejte na stránce MK.",
      "access_url": "https://mk.gov.cz/evidence-knihoven-adresar-knihoven-evidovanych-ministerstvem-kultury-a-souvisejici-informace-cs-341"
      /* "download_url": "TODO" */
    }
  }
}

```
#### JSON scheme for libraries according to our dataset
```
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "EvidenceKnihovenSchema",
  "type": "array",
  "description": "Seznam knihoven evidovaných Ministerstvem kultury (array knihovních záznamů)",
  "items": {
    "type": "object",
    "description": "Záznam jedné knihovny v evidenci",
    "properties": {
      "nazev_knihovny": {
        "type": "string",
        "description": "Název knihovny"
      },
      "evidencni_cislo": {
        "type": "string",
        "description": "Evidenční číslo knihovny (unikátní registrační číslo)",
        "pattern": "^[0-9]+/[0-9]{4}$"
      },
      "adresa": {
        "type": "object",
        "description": "Adresa knihovny",
        "properties": {
          "ulice": {
            "type": "string",
            "description": "Ulice a číslo popisné"
          },
          "mesto": {
            "type": "string",
            "description": "Město nebo obec"
          },
          "psc": {
            "type": "string",
            "description": "PSČ (poštovní směrovací číslo)",
            "pattern": "^[0-9]{3}\\s?[0-9]{2}$"
          },
          "kraj": {
            "type": "string",
            "description": "Kraj (region)",
            "examples": ["Hlavní město Praha", "Jihomoravský kraj"]
          }
        },
        "required": ["ulice", "mesto", "psc", "kraj"],
        "additionalProperties": false
      },
      "pravni_forma": {
        "type": "string",
        "description": "Právní forma organizace knihovny"
      },
      "typ_knihovny": {
        "type": "string",
        "description": "Typ (druh) knihovny"
      },
      "zrizovatel": {
        "type": "string",
        "description": "Zřizovatel knihovny (zakladatel/provozovatel)"
      },
      "kontaktni_udaje": {
        "type": "object",
        "description": "Kontaktní údaje knihovny",
        "properties": {
          "telefon": {
            "type": "string",
            "description": "Telefonní číslo",
            "pattern": "^[+]?[0-9 ]+$"
          },
          "email": {
            "type": "string",
            "format": "email",
            "description": "E-mailová adresa"
          },
          "web": {
            "type": "string",
            "format": "uri",
            "description": "Webové stránky knihovny (URL)"
          }
        },
        "additionalProperties": false
      },
      "datum_evidence": {
        "type": "string",
        "format": "date",
        "description": "Datum evidence knihovny (datum registrace v evidenci)"
      }
    },
    "required": [
      "nazev_knihovny",
      "evidencni_cislo",
      "adresa",
      "pravni_forma",
      "typ_knihovny",
      "zrizovatel",
      "kontaktni_udaje",
      "datum_evidence"
    ],
    "additionalProperties": false
  }
}


```
