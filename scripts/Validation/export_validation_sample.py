import os
import shutil
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))

SOURCE_IMAGES = os.path.join(PROJECT_ROOT, "data", "training", "raw")
SOURCE_LABELS = os.path.join(PROJECT_ROOT, "data", "training", "labels")
DEST_IMAGES = os.path.join(PROJECT_ROOT, "data", "test_training", "images")
DEST_LABELS = os.path.join(PROJECT_ROOT, "data", "test_training", "labels")
SAMPLE_SIZE = 100

os.makedirs(DEST_IMAGES, exist_ok=True)
os.makedirs(DEST_LABELS, exist_ok=True)

# Collect all labeled image base names
label_basenames = [
    os.path.splitext(f)[0]
    for f in os.listdir(SOURCE_LABELS)
    if f.endswith(".txt")
]

sampled = random.sample(label_basenames, min(SAMPLE_SIZE, len(label_basenames)))
copied = 0

for name in sampled:
    image_found = False
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        img_path = os.path.join(SOURCE_IMAGES, name + ext)
        if os.path.exists(img_path):
            shutil.copy2(img_path, os.path.join(DEST_IMAGES, name + ext))
            image_found = True
            break

    label_path = os.path.join(SOURCE_LABELS, name + ".txt")
    if os.path.exists(label_path):
        shutil.copy2(label_path, os.path.join(DEST_LABELS, name + ".txt"))

    if image_found:
        copied += 1

print(f"🔎 Exported {copied} labeled image/label pairs to `test_training/` for validation.")