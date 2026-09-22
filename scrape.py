import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os
from datetime import datetime

# ---- SETTINGS: change these to match what you're looking for ----
KEYWORDS = ["virtual assistant", "executive assistant"]  # add/remove keywords here
PAGES_PER_KEYWORD = 3  # 30 jobs per page
# -------------------------------------------------------------------

BASE = "https://www.onlinejobs.ph/jobseekers/jobsearch"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"}

jobs = {}

for keyword in KEYWORDS:
    for page in range(PAGES_PER_KEYWORD):
        offset = page * 30
        kw = keyword.replace(" ", "+")
        url = f"{BASE}/{offset}?jobkeyword={kw}" if offset > 0 else f"{BASE}?jobkeyword={kw}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
        except Exception as e:
            print(f"Request failed for {keyword} page {page+1}: {e}")
            continue

        print(f"[{keyword}] Page {page+1}: status {resp.status_code}")
        if resp.status_code != 200:
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", href=re.compile(r"/jobseekers/job/"))
        if not links:
            print("No listings found — stopping this keyword.")
            break

        for link in links:
            href = link.get("href")
            full_url = href if href.startswith("http") else "https://www.onlinejobs.ph" + href
            text = link.get_text(strip=True)
            if full_url not in jobs:
                jobs[full_url] = {"url": full_url, "snippets": [], "keyword": keyword}
            if text:
                jobs[full_url]["snippets"].append(text)

        time.sleep(2)

rows = []
for url, data in jobs.items():
    snippets = list(dict.fromkeys(data["snippets"]))  # dedupe preserving order
    if not snippets:
        continue
    snippets_sorted = sorted(set(snippets), key=len, reverse=True)
    title_line = min(snippets_sorted, key=len) if len(snippets_sorted) > 1 else snippets_sorted[0]
    description = snippets_sorted[0]
    rows.append({
        "url": url,
        "title_line": title_line,
        "description": description,
        "keyword": data["keyword"],
        "scraped_at": datetime.utcnow().isoformat()
    })

os.makedirs("data", exist_ok=True)
outfile = "data/jobs_latest.csv"
with open(outfile, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["url", "title_line", "description", "keyword", "scraped_at"])
    writer.writeheader()
    writer.writerows(rows)

print(f"\nDone. Found {len(rows)} unique listings. Saved to {outfile}")
