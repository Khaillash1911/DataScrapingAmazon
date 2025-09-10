# src/collect.py

import requests
import time
import random
import pandas as pd
from bs4 import BeautifulSoup

BASE_URL = "https://www.amazon.com/Best-Sellers-Health-Personal-Care-Vitamins-Dietary-Supplements/zgbs/hpc/3764441"

# Rotate user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9"
    }

def fetch_page(url):
    """Fetch a single Amazon page with retry + backoff for 429 errors."""
    while True:
        r = requests.get(url, headers=get_headers())
        if r.status_code == 200:
            return BeautifulSoup(r.text, "html.parser")
        elif r.status_code == 429:
            wait_time = random.randint(10, 20)
            print(f"⚠️ Got 429 Too Many Requests. Waiting {wait_time}s...")
            time.sleep(wait_time)
        else:
            print(f"❌ Failed with status {r.status_code}")
            r.raise_for_status()

def parse_products(soup):
    """Extract product info (Title, Price, Star Rating) from a page and truncate long titles."""
    products = []
    items = soup.select("div.p13n-sc-uncoverable-faceout")  # container for each product

    for item in items:
        # Extract elements
        title_element = item.select_one("div._cDEzb_p13n-sc-css-line-clamp-3_g3dy1")  # title
        price_element = item.select_one("span.p13n-sc-price")  # price
        star_element = item.select_one("span.a-icon-alt")  # star rating

        # Get text
        title = title_element.get_text(strip=True) if title_element else None
        price = price_element.get_text(strip=True) if price_element else None
        star = star_element.get_text(strip=True) if star_element else None

        # Truncate title at first ',', '|', or '-'
        if title:
            for sep in [',', '|', '-']:
                if sep in title:
                    title = title.split(sep)[0].strip()
                    break

        products.append({
            "Title": title,
            "Price": price,
            "Star Rating": star,
        })

    return products


def collect_products(max_pages=2):
    """Scrape multiple Amazon bestseller pages."""
    all_products = []

    for page in range(1, max_pages + 1):
        url = BASE_URL + f"?pg={page}"
        print(f"🔎 Scraping {url}")
        soup = fetch_page(url)
        products = parse_products(soup)
        all_products.extend(products)

        # Random delay between page requests
        delay = random.randint(5, 10)
        print(f"⏳ Waiting {delay}s before next page...")
        time.sleep(delay)

    df = pd.DataFrame(all_products).dropna(subset=["Title"])
    return df
