import hashlib, os, re, sys, time
from datetime import date
import requests
from bs4 import BeautifulSoup

PURL = "https://mk.gov.cz/evidence-knihoven-adresar-knihoven-evidovanych-ministerstvem-kultury-a-souvisejici-informace-cs-341"
OUT_DIR = "downloads"

def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    hdrs = {"User-Agent": "CZ-Libraries-Harvester/1.0 (+contact: you@example.com)"}
    html = requests.get(PURL, headers=hdrs, timeout=30)
    html.raise_for_status()
    soup = BeautifulSoup(html.text, "html.parser")

    # searching for .xlsx (somewhere near 'Databáze knihoven')
    link = None
    # 1) pokus přes text
    for a in soup.find_all("a", href=True):
        if ".xlsx" in a["href"].lower() and ("Databáze" in a.get_text() or "knihoven" in a.get_text()):
            link = a["href"]; break
    # 2) fallback: first .xlsx on the page
    if not link:
        for a in soup.find_all("a", href=True):
            if a["href"].lower().endswith(".xlsx"):
                link = a["href"]; break
    if not link:
        raise RuntimeError("Link to XLSX file was not found.")

    if link.startswith("/"):
        base = "https://mk.gov.cz"
        link = base + link

    r = requests.get(link, headers=hdrs, timeout=60)
    r.raise_for_status()
    content = r.content
    digest = sha256_bytes(content)
    today = date.today().isoformat()
    versioned = os.path.join(OUT_DIR, f"library-records{today}.xlsx")
    latest = os.path.join(OUT_DIR, "library-records_latest.xlsx")

    if os.path.exists(versioned):
        print("WARNING: Today's version is already downloaded.")
        return

    with open(versioned, "wb") as f:
        f.write(content)
    # latest
    with open(latest, "wb") as f:
        f.write(content)

    with open(versioned + ".sha256", "w", encoding="utf-8") as f:
        f.write(digest + "  " + os.path.basename(versioned) + "\n")

    print("Saved:", versioned)
    print("SHA256:", digest)

if __name__ == "__main__":
    main()
