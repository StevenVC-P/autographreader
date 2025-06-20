import os
import sqlite3
import hashlib
import requests

# Use project-root-relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))

DB_PATH = os.path.join(PROJECT_ROOT, "database", "autographs.db")
EXPORT_DIR = os.path.join(PROJECT_ROOT, "qa_review", "raw")
EXPORT_LOG = os.path.join(PROJECT_ROOT, "database", "exported.txt")

HEADERS = {"User-Agent": "Mozilla/5.0"}

def sanitize_ext(url):
    ext = os.path.splitext(url)[1].split('?')[0].lower()
    return ext if ext in [".jpg", ".jpeg", ".png", ".webp"] else ".jpg"

def export_images():
    os.makedirs(EXPORT_DIR, exist_ok=True)

    exported_urls = set()
    if os.path.exists(EXPORT_LOG):
        with open(EXPORT_LOG, "r") as f:
            exported_urls = set(line.strip() for line in f)

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT title, signer_id, img_url FROM autographs WHERE img_url IS NOT NULL")
        rows = c.fetchall()

        for title, signer_id, img_url in rows:
            if not img_url.startswith("http"):
                print(f"⚠️ Skipping invalid URL: {img_url}")
                continue
            if img_url in exported_urls:
                print(f"⏭️ Already exported: {img_url}")
                continue

            try:
                response = requests.get(img_url, headers=HEADERS, stream=True, timeout=10)
                if response.status_code == 200:
                    hash_id = hashlib.md5(img_url.encode()).hexdigest()
                    ext = sanitize_ext(img_url)
                    filename = f"{hash_id}_signer{signer_id}{ext}"
                    filepath = os.path.join(EXPORT_DIR, filename)

                    with open(filepath, "wb") as out:
                        for chunk in response.iter_content(1024):
                            out.write(chunk)

                    print(f"✅ Downloaded: {filename}")

                    with open(EXPORT_LOG, "a") as f:
                        f.write(img_url + "\n")
                else:
                    print(f"❌ Failed to fetch: {img_url} (HTTP {response.status_code})")
            except Exception as e:
                print(f"❌ Error fetching {img_url}: {e}")

    print(f"\n🎯 QA image export complete. Check {EXPORT_DIR}")

if __name__ == "__main__":
    export_images()
