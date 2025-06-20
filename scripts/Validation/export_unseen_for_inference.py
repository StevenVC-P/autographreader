import os
import shutil

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))

SOURCE_IMAGES = os.path.join(PROJECT_ROOT, "data", "training", "raw")
SOURCE_LABELS = os.path.join(PROJECT_ROOT, "data", "training", "labels")
DEST_IMAGES = os.path.join(PROJECT_ROOT, "data", "unseen_eval", "images")

CUTOFF_FILENAME = "2424_signer3_32ea09cdbe50462a0e27038046e3dc47.txt"
SAMPLE_AFTER = 100  # number of post-cutoff examples to copy

# Ensure destination exists
os.makedirs(DEST_IMAGES, exist_ok=True)

# Sort all label filenames
label_files = sorted(
    f for f in os.listdir(SOURCE_LABELS)
    if f.endswith(".txt")
)

# Find index just after the cutoff
try:
    cutoff_index = label_files.index(CUTOFF_FILENAME)
except ValueError:
    print(f"❌ Cutoff file {CUTOFF_FILENAME} not found.")
    exit(1)

post_cutoff_files = label_files[cutoff_index + 1:cutoff_index + 1 + SAMPLE_AFTER]
exported = 0

for label_file in post_cutoff_files:
    base = os.path.splitext(label_file)[0]

    # Look for matching image
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        img_path = os.path.join(SOURCE_IMAGES, base + ext)
        if os.path.exists(img_path):
            shutil.copy2(img_path, os.path.join(DEST_IMAGES, base + ext))
            exported += 1
            break  # found image, no need to check more extensions

print(f"🔎 Exported {exported} unseen images to `data/unseen_eval/images/` for inference.")
