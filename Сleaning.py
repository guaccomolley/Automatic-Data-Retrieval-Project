import pandas as pd
import numpy as np
import re
import unicodedata

# help functions

def normalize_ico(ico):
    """IČO jako 8místný string; jinak NaN."""
    if pd.isna(ico):
        return pd.NA
    s = str(ico).strip()
    return s.zfill(8) if s.isdigit() else pd.NA

def normalize_ws(s: pd.Series) -> pd.Series:

    s = s.replace(["nan", "NaN", "NAN"], pd.NA).astype("string")
    return s.str.replace(r"\s+", " ", regex=True).str.strip()

def strip_diacritics(x):
    if pd.isna(x):
        return pd.NA
    nf = unicodedata.normalize("NFD", str(x))
    return "".join(ch for ch in nf if unicodedata.category(ch) != "Mn")

def fix_url(url):
    if pd.isna(url):
        return pd.NA
    url = str(url).strip()
    if not url or url.lower() == "nan":
        return pd.NA
    if url.lower().startswith(("http://", "https://", "www.")):
        return url
    if re.match(r"^[\w\.-]+\.[a-z]{2,}$", url, re.IGNORECASE):
        return url
    return pd.NA

def normalize_psc(x):
    """Vrátí pět číslic PSČ, jinak NaN."""
    if pd.isna(x):
        return pd.NA
    m = re.search(r"\b(\d{3})\s?(\d{2})\b", str(x))
    return (m.group(1) + m.group(2)) if m else pd.NA



df = pd.read_excel("downloads/library-records_latest.xlsx")
# dict with keys as original names and values as new names
rename_map = {
    "R - EVIDENČNÍ ČÍSLO KNIHOVNY": "evidencni_cislo",
    "I - NÁZEV KNIHOVNY": "nazev_knihovny",
    "Název provozovatele": "nazev_provozovatele",
    "B/H - IČ provozovatele (u fyzické osoby pokud bylo přiděleno)": "ico_provozovatele",
    "G - IČ zřizovatele": "ico_zrizovatele",

    "C/CH - sídlo/adresa; místo trvalého pobytu fyz. osoby - ulice": "sidlo_ulice",
    "C/CH - sídlo/adresa; místo trvalého pobytu fyz. osoby - PSČ": "sidlo_psc",
    "C/CH - sídlo/adresa; místo trvalého pobytu fyz. osoby - obec": "sidlo_obec",
    "C/CH - sídlo/adresa; místo trvalého pobytu fyz. osoby - okres": "sidlo_okres",
    "C/CH - sídlo/adresa; místo trvalého pobytu fyz. osoby - kraj": "sidlo_kraj",

    "K - adresa knihovny: ulice": "knihovna_ulice",
    "K - adresa knihovny: PSČ": "knihovna_psc",
    "K - adresa knihovny: město": "knihovna_mesto",
    "K - adresa knihovny: okres": "knihovna_okres",
    "K - adresa knihovny: kraj": "knihovna_kraj",

    "O - odkaz na webovou stránku knihovny, respektive odkaz na informace o knihovně na webových stránkách provozovatele": "web_knihovna",
    "N - e-mailový kontakt na knihovnu": "email_knihovna",

    "S - datum vytvoření záznamu": "datum_vytvoreni",
    "T - datum evidence knihovny": "datum_evidence",
    "U - datum aktualizace záznamu": "datum_aktualizace",
    "V - datum vyřazení": "datum_vyrazeni",

    "aktivní / zrušená (vyřazená z evidence)": "stav",
    "Poznámka": "poznamka",
}
df = df.rename(columns=rename_map)
# data cleaning

if "ico_provozovatele" in df.columns:
    df["ico_provozovatele"] = df["ico_provozovatele"].apply(normalize_ico).astype("string")
if "ico_zrizovatele" in df.columns:
    df["ico_zrizovatele"] = df["ico_zrizovatele"].apply(normalize_ico).astype("string")

if "email_knihovna" in df.columns:
    df["email_knihovna"] = normalize_ws(df["email_knihovna"]).str.lower()

if "web_knihovna" in df.columns:
    df["web_knihovna"] = df["web_knihovna"].apply(fix_url).astype("string")

if "knihovna_psc" in df.columns:
    df["knihovna_psc"] = df["knihovna_psc"].apply(normalize_psc).astype("string")

for c in ["datum_vytvoreni","datum_evidence","datum_aktualizace","datum_vyrazeni"]:
    if c in df.columns:
        df[c] = pd.to_datetime(df[c], errors="coerce")

# ASCII additional columns

ascii_cols = {
    "nazev_knihovny": "nazev_ascii",
    "knihovna_ulice": "adresa_ascii",
    "knihovna_mesto": "mesto_ascii"
}
for src_col, new_col in ascii_cols.items():
    if src_col in df.columns:
        df[new_col] = (
            normalize_ws(df[src_col])
            .apply(strip_diacritics)
            .str.lower()
            .astype("string")
        )

if "nazev_knihovny" in df.columns:
    df["nazev_lower"] = normalize_ws(df["nazev_knihovny"]).str.lower().astype("string")

# merging data types
text_cols = [
    "nazev_knihovny","nazev_provozovatele","email_knihovna","web_knihovna",
    "knihovna_ulice","knihovna_mesto","knihovna_okres","knihovna_kraj",
    "nazev_lower","nazev_ascii","adresa_ascii","mesto_ascii"
]
for c in text_cols:
    if c in df.columns:
        df[c] = df[c].astype("string")

df.to_csv("library-records_clean.csv", index=False, sep=";", encoding="utf-8-sig")

