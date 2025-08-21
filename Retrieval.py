import hashlib, os, re, sys, time
import logging
from datetime import date
import requests
from bs4 import BeautifulSoup

PURL = "https://mk.gov.cz/evidence-knihoven-adresar-knihoven-evidovanych-ministerstvem-kultury-a-souvisejici-informace-cs-341"
OUT_DIR = "downloads"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",  # timestamp + level + message
    datefmt="%Y-%m-%d %H:%M:%S"
)

def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256(); h.update(b); return h.hexdigest()

def get_previous_sha256(latest_path: str):
    """Vrátí SHA256 z posledního staženého souboru (pokud existuje)."""
    if os.path.exists(latest_path):
        with open(latest_path, "rb") as f:
            return sha256_bytes(f.read())
    return None

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    html = requests.get(PURL, timeout=30)
    html.raise_for_status()
    soup = BeautifulSoup(html.text, "html.parser")

    # searching for .xlsx (somewhere near 'Databáze knihoven')
    link = None
    # 1) through text:
    for a in soup.find_all("a", href=True):
        if ".xlsx" in a["href"].lower() and ("Databáze" in a.get_text() or "knihoven" in a.get_text()):
            link = a["href"]; break
    # 2) than first .xlsx on the page
    if not link:
        for a in soup.find_all("a", href=True):
            if a["href"].lower().endswith(".xlsx"):
                link = a["href"]; break
    if not link:
        logging.error("Link to XLSX file was not found.")
        raise RuntimeError("Link to XLSX file was not found.")

    if link.startswith("/"):
        base = "https://mk.gov.cz"
        link = base + link

    r = requests.get(link, timeout=60)
    r.raise_for_status()
    content = r.content
    digest = sha256_bytes(content)
    today = date.today().isoformat()
    versioned = os.path.join(OUT_DIR, f"library-records{today}.xlsx")
    latest = os.path.join(OUT_DIR, "library-records_latest.xlsx")

    prev_hash = get_previous_sha256(latest)
    if prev_hash:
        if prev_hash == digest:
            logging.warning("New version has the same SHA256, the content is the same.")
        else:
            logging.info("New version differs from the previous.")
    else:
        logging.info("Previous version wasn't found.")

        return

    with open(versioned, "wb") as f:
        f.write(content)
    # latest
    with open(latest, "wb") as f:
        f.write(content)

    with open(versioned + ".sha256", "w", encoding="utf-8") as f:
        f.write(digest + "  " + os.path.basename(versioned) + "\n")

    logging.info(f"Saved: {versioned}")
    logging.info(f"Saved: {digest}")

if __name__ == "__main__":
    main()
