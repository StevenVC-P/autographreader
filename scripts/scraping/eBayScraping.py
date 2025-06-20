import requests
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse, urlunparse, parse_qs
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import time
import sqlite3
import os
import re
import json

from scrapeHelper import apply_scrape_options, get_random_proxy, get_random_user_agent, test_proxy_connectivity

# Before initializing driver:
proxy = get_random_proxy()
user_agent = get_random_user_agent()
print(f"🌟 Using proxy: {proxy}")
print(f"🧠 Using User-Agent: {user_agent}")

options = uc.ChromeOptions()
options = apply_scrape_options(options, proxy=proxy, user_agent=user_agent)
driver = uc.Chrome(version_main=136, options=options)

sqlite3.register_adapter(datetime, lambda val: val.isoformat())
sqlite3.register_converter("timestamp", lambda val: datetime.fromisoformat(val.decode("utf-8")))

# --- Constants ---
CONFIG_DIR = "config"
DB_PATH = os.path.join("database", "autographs.db")
CACHE_FILE = os.path.join(CONFIG_DIR, "signer_cache.json")
KNOWN_SIGNERS_FILE = os.path.join(CONFIG_DIR, "known_signers.json")
BASE_SEARCH_URL = "https://www.ebay.com/sch/i.html?_nkw={query}&_sacat={category_id}&_pgn={page}"
SEARCH_QUERY = "autograph"
WIKIDATA_SEARCH_URL = "https://www.wikidata.org/w/api.php"
MAX_RESULTS = 5000
HEADERS = {"User-Agent": "Mozilla/5.0"}

CATEGORY_MAP = {
    "sports_mem": "64482",
    # "entertainment_mem": "45100",
    # "collectibles": "1",
    # "art": "550",
    # "books": "267",
    # "music": "11233",
    # "autographs_original": "51",
    # "autographs_reprints": "50115",
    # "movie_memorabilia": "45100",
    # "political_memorabilia": "13905",
    # "theater_memorabilia": "45100",
    # "video_game_memorabilia": "45101",
    # "historical_memorabilia": "39507",
    # "militaria": "13956",
    # "paper_americana": "593",
    # "postcards": "914",
    # "ephemera": "26364",
    # "presidential_memorabilia": "14007",
    # "documents_maps": "13871",
    # "trading_cards_nonsport": "183050",
    # "philately": "260"
}

wikidata_cache = {}
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        wikidata_cache = json.load(f)

def load_known_signers(path=KNOWN_SIGNERS_FILE):
    with open(path, "r", encoding="utf-8") as f:
        return set(json.load(f))

known_signers = load_known_signers()

def normalize_phrase(text):
    return re.sub(r'\W+', ' ', text).strip().lower()

def validate_with_wikidata(name):
    print(f"🔎 Validating name with Wikidata: {name}")
    normalized = normalize_phrase(name)

    if normalized in wikidata_cache:
        result = wikidata_cache[normalized]
        print(f"⚡ Cache hit: {normalized} → {result}")
        return result, 0.75 if result != "Unknown" else 0.0

    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": name
    }

    try:
        response = requests.get(WIKIDATA_SEARCH_URL, params=params, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            results = response.json().get("search", [])
            if results:
                top_result = results[0]
                canonical_name = top_result.get("label", "").strip()
                if canonical_name:
                    wikidata_cache[normalized] = canonical_name
                    print(f"✅ Match: {name} → {canonical_name}")
                    return canonical_name, 0.75
    except Exception as e:
        print(f"❌ Wikidata request failed: {e}")

    wikidata_cache[normalized] = "Unknown"
    return "Unknown", 0.0

def detect_signer(title):
    title_lower = title.lower()
    for name in known_signers:
        if name in title_lower:
            return name, 1.0
    return validate_with_wikidata(title)

def build_url(query, category_id, page=1):
    return BASE_SEARCH_URL.format(query=query, category_id=category_id, page=page)

def normalize_listing_url(url):
    try:
        parsed = urlparse(url)
        clean_path = parsed.path  # strip query params
        return urlunparse((parsed.scheme, parsed.netloc, clean_path, '', '', ''))
    except Exception:
        return url.strip().split('?')[0]

def page_already_scraped(listing_urls, db_path="database/autographs.db"):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        placeholders = ','.join('?' for _ in listing_urls)
        c.execute(f"SELECT listing_url FROM autographs WHERE listing_url IN ({placeholders})", listing_urls)
        found = set(row[0] for row in c.fetchall())
        return found

def should_skip_page(listings_on_page):
    urls = [item['listing_url'] for item in listings_on_page if item['listing_url']]
    existing = page_already_scraped(urls)
    return len(existing) == len(urls)

def scrape_page(query, category, page, retries=3):
    url = build_url(query, CATEGORY_MAP[category], page)
    print(f"Scraping {category} page {page} — URL: {url}")

    user_agent = get_random_user_agent()
    print(f"🧠 Using User-Agent: {user_agent}")

    for attempt in range(1, retries + 1):
        driver = None
        try:
            options = uc.ChromeOptions()
            options = apply_scrape_options(options, proxy=None, user_agent=user_agent)
            driver = uc.Chrome(version_main=136, options=options)
            driver.set_page_load_timeout(20)
            driver.get(url)

            print("📄 Page loaded, attempting to scroll to trigger rendering...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)

            # Extra anti-bot measure: simulate slight human behavior
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
            time.sleep(1)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "s-item"))
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")
            items = soup.select(".s-item")

            data = []
            for item in items:
                title = item.select_one(".s-item__title")
                price = item.select_one(".s-item__price")
                link = item.select_one(".s-item__link")
                img_tag = item.select_one(".s-item__image-img") or item.select_one("img")
                img_url = img_tag.get("src") if img_tag else None

                if not title or not title.get_text(strip=True): continue
                if "listing" in title.get_text(strip=True).lower(): continue
                if not img_url: continue

                signer_name, confidence = detect_signer(title.get_text())
                data.append({
                    "title": title.get_text(),
                    "price": price.get_text() if price else "N/A",
                    "img_url": img_url,
                    "listing_url": link["href"] if link else None,
                    "category": category,
                    "signer": signer_name,
                    "confidence": confidence
                })

            return data

        except Exception as e:
            print(f"❌ Selenium error on attempt {attempt}: {e}")
            import traceback
            traceback.print_exc()
            if attempt == retries:
                print("⛔️ Giving up on this page.")
                return []
            time.sleep(60)

        finally:
            if driver:
                try: driver.quit()
                except: pass

def scrape_autographs(query=SEARCH_QUERY, categories=list(CATEGORY_MAP.keys())):
    all_data = []
    for category in categories:
        print(f"\n🔎 Starting category: {category}")
        page = 1
        consecutive_failures = 0
        max_consecutive_failures = 3

        while True:
            if len(all_data) >= MAX_RESULTS:
                print(f"🚫 Reached max result cap: {MAX_RESULTS}")
                return all_data[:MAX_RESULTS]

            page_data = scrape_page(query, category, page)
            if not page_data:
                consecutive_failures += 1
                print(f"📉 No listings found or error on page {page}. Failure count: {consecutive_failures}")
                if consecutive_failures >= max_consecutive_failures:
                    print(f"📉 No more results for {category} after page {page}.")
                    break
            else:
                consecutive_failures = 0
                if should_skip_page(page_data):
                    print(f"⏭️ Skipping page {page} — all listings already known")
                else:
                    all_data.extend(page_data)
                    save_to_db(page_data, run_id)

            page += 1
            time.sleep(30)

    return all_data[:MAX_RESULTS]

def init_db():
    if not os.path.exists(DB_PATH):
        print("🢨 Creating new database (initial setup)")
    else:
        print("🛡️ Using existing database — no data will be lost")

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS signers (
            id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            category TEXT NOT NULL,
            birth_year INTEGER,
            active_years TEXT,
            nationality TEXT,
            notable_works TEXT,
            deceased BOOLEAN,
            UNIQUE(full_name, category))''')

        c.execute('''CREATE TABLE IF NOT EXISTS autographs (
            id INTEGER PRIMARY KEY,
            title TEXT,
            price TEXT,
            img_url TEXT,
            listing_url TEXT UNIQUE,
            category TEXT,
            signer_id INTEGER,
            confidence REAL,
            last_seen TIMESTAMP,
            run_id INTEGER,
            FOREIGN KEY (signer_id) REFERENCES signers(id),
            FOREIGN KEY (run_id) REFERENCES scrape_runs(id))''')

        c.execute('''CREATE TABLE IF NOT EXISTS scrape_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT)''')

def create_scrape_run():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO scrape_runs (notes) VALUES (?)", ("Americana scrape",))
        return c.lastrowid

def get_or_create_signer(conn, name, category):
    c = conn.cursor()
    c.execute("SELECT id FROM signers WHERE full_name = ? AND category = ?", (name, category))
    row = c.fetchone()
    if row:
        return row[0]
    try:
        c.execute("INSERT INTO signers (full_name, category) VALUES (?, ?)", (name, category))
        return c.lastrowid
    except sqlite3.IntegrityError:
        c.execute("SELECT id FROM signers WHERE full_name = ? AND category = ?", (name, category))
        return c.fetchone()[0]

def save_to_db(data, run_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        saved = 0
        now = datetime.now(timezone.utc)

        for item in data:
            if item["signer"] == "Unknown":
                continue

            signer_id = get_or_create_signer(conn, item["signer"], item["category"])

            c.execute("SELECT id FROM autographs WHERE listing_url = ?", (item["listing_url"],))
            existing = c.fetchone()

            if existing:
                c.execute('''UPDATE autographs
                             SET last_seen = ?, run_id = ?
                             WHERE listing_url = ?''',
                          (now, run_id, item["listing_url"]))
                continue

            c.execute('''INSERT INTO autographs (
                            title, price, img_url, listing_url,
                            category, signer_id, confidence,
                            last_seen, run_id)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (item['title'], item['price'], item['img_url'],
                       item['listing_url'], item['category'],
                       signer_id, item['confidence'], now, run_id))
            saved += 1

        print(f"✅ {saved} new records saved (others updated with last_seen).")

if __name__ == "__main__":
    init_db()
    run_id = create_scrape_run()
    data = scrape_autographs()
    save_to_db(data, run_id)

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(wikidata_cache, f, indent=2, ensure_ascii=False)

    print("All done!")
