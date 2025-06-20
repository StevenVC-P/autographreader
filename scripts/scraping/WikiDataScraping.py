import requests
import time
import json
import os

HEADERS = {
    "User-Agent": "AutographReaderBot/1.0 (mailto:your-email@example.com)"
}

CONFIG_DIR = "config"
SIGNER_FILE = os.path.join(CONFIG_DIR, "known_signers.json")
META_FILE = os.path.join(CONFIG_DIR, "signers_meta.json")

OCCUPATION_QID_MAP = {
    # "actor": "Q33999",
    # "musician": "Q639669",
    # "singer": "Q177220",
    # "composer": "Q36834",
    # "writer": "Q36180",
    # "author": "Q482980",
    # "journalist": "Q1930187",
    # "politician": "Q82955",
    # "president": "Q11696",
    # "governor": "Q179978",
    "athlete": "Q2066131",
    "professional_wrestler": "Q2309784",
    "baseball_player": "Q10833314",
    "american_football_player": "Q3665646",
    "coach": "Q41583",
    # "television_personality": "Q947873",
    # "film_director": "Q2526255"
}


def fetch_known_signers(limit_per_page=250, retries=3, backoff=2, full_refresh=False):
    occupation_filter = ", ".join(f"wd:{qid}" for qid in OCCUPATION_QID_MAP.values())

    # Load existing signer list and metadata
    if not full_refresh and os.path.exists(SIGNER_FILE):
        with open(SIGNER_FILE, "r", encoding="utf-8") as f:
            all_names = set(json.load(f))
        start_page = 1
        if os.path.exists(META_FILE):
            with open(META_FILE, "r", encoding="utf-8") as f:
                meta = json.load(f)
                start_page = meta.get("last_page", 1)
        print(f"🔁 Incremental update starting from page {start_page}")
    else:
        all_names = set()
        start_page = 0
        print("🧼 Full refresh — starting from page 0")

    page = start_page
    consecutive_skips = 0
    max_skips = 5

    while True:
        offset = page * limit_per_page
        query = f"""
        SELECT DISTINCT ?personLabel WHERE {{
            ?person wdt:P31 wd:Q5;
                    wdt:P106 ?occupation;
                    wdt:P27 wd:Q30.  # Only U.S. citizens
            FILTER(?occupation IN ({occupation_filter}))
            SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
        }}
        LIMIT {limit_per_page}
        OFFSET {offset}
        """

        page_results = set()
        success = False

        for attempt in range(retries):
            try:
                response = requests.get(
                    "https://query.wikidata.org/sparql",
                    params={"query": query, "format": "json"},
                    headers=HEADERS,
                    timeout=60
                )
                if response.status_code == 200:
                    data = response.json()
                    page_results = {
                        item["personLabel"]["value"].strip().lower()
                        for item in data["results"]["bindings"]
                        if "personLabel" in item
                    }
                    print(f"✅ Page {page}: {len(page_results)} signers")
                    all_names.update(page_results)
                    success = True

                    # Save after each successful page
                    with open(SIGNER_FILE, "w", encoding="utf-8") as f:
                        json.dump(sorted(all_names), f, indent=2, ensure_ascii=False)
                    with open(META_FILE, "w", encoding="utf-8") as f:
                        json.dump({"last_page": page + 1}, f, indent=2)

                    break
                else:
                    print(f"⚠️ HTTP {response.status_code} on attempt {attempt + 1}")
            except Exception as e:
                print(f"⚠️ Attempt {attempt + 1} failed: {e}")
            time.sleep(backoff * (attempt + 1))

        if not success:
            print(f"⏭️ Skipping page {page} after {retries} failed attempts.")
            consecutive_skips += 1
            if consecutive_skips >= max_skips:
                print(f"🛑 Aborting: {consecutive_skips} pages skipped in a row.")
                break
        elif len(page_results) < limit_per_page:
            print(f"📉 Page {page} had fewer than {limit_per_page} entries — stopping.")
            break
        else:
            consecutive_skips = 0

        page += 1
        time.sleep(1)

    print(f"✅ Final signer count: {len(all_names)}")
    return all_names

# Optional CLI entry
if __name__ == "__main__":
    fetch_known_signers()
