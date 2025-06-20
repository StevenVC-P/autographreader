# export_for_labeling.py — Prepares new images for manual box labeling or pretraining
# Purpose: Export unmarked images from DB into training/raw for labelImg or pretraining

import os
import sqlite3
import hashlib
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))

DB_PATH = os.path.join(PROJECT_ROOT, "database", "autographs.db")
EXPORT_DIR = os.path.join(PROJECT_ROOT, "data", "training", "raw")
EXPORT_LOG = os.path.join(PROJECT_ROOT, "data", "training", "exported_training.txt")
LIMIT = 200

HEADERS = {"User-Agent": "Mozilla/5.0"}

def sanitize_ext(url):
    ext = os.path.splitext(url)[1].split('?')[0].lower()
    return ext if ext in [".jpg", ".jpeg", ".png", ".webp"] else ".jpg"

def export_training_images():
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    # Load already-exported URLs
    exported_urls = set()
    if os.path.exists(EXPORT_LOG):
        with open(EXPORT_LOG, "r") as f:
            exported_urls = set(line.strip() for line in f)

    # Get unexported image URLs from DB
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT MIN(signer_id), img_url
            FROM autographs
            WHERE signer_id IS NOT NULL AND img_url IS NOT NULL
            GROUP BY img_url
        """)
        rows = [row for row in c.fetchall() if row[1] not in exported_urls]

        print(f"🧪 Found {len(rows)} unexported images.")
        to_export = rows[:LIMIT]

        for i, (signer_id, img_url) in enumerate(to_export):
            if not img_url.startswith("http"):
                print(f"⚠️ Skipping invalid URL: {img_url}")
                continue

            try:
                response = requests.get(img_url, headers=HEADERS, stream=True, timeout=10)
                if response.status_code == 200:
                    hash_id = hashlib.md5(img_url.encode()).hexdigest()
                    ext = sanitize_ext(img_url)
                    filename = f"{i:03d}_signer{signer_id}_{hash_id}{ext}"
                    filepath = os.path.join(EXPORT_DIR, filename)

                    with open(filepath, "wb") as out:
                        for chunk in response.iter_content(1024):
                            out.write(chunk)

                    # Save img_url to log filec.ex
                    with open(EXPORT_LOG, "a") as f:
                        f.write(img_url + "\n")

                    print(f"✅ Downloaded: {filename}")
                else:
                    print(f"❌ Failed to fetch: {img_url} (HTTP {response.status_code})")
            except Exception as e:
                print(f"❌ Error fetching {img_url}: {e}")

    print(f"\n🎯 Export complete. Check {EXPORT_DIR}")

if __name__ == "__main__":
    export_training_images()
