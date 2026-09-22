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

        print(f"[{keyword}] Page {page+1}: status
