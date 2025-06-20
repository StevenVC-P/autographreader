import os
import shutil

# Root-relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))

SOURCE_IMAGES = os.path.join(PROJECT_ROOT, "data", "training", "raw")
SOURCE_LABELS = os.path.join(PROJECT_ROOT, "data", "training", "labels")
DEST_IMAGES = os.path.join(PROJECT_ROOT, "yolo_dataset", "train", "images")
DEST_LABELS = os.path.join(PROJECT_ROOT, "yolo_dataset", "train", "labels")

# Only move label/image pairs up to this filename
CUTOFF_FILENAME = "2424_signer3_32ea09cdbe50462a0e27038046e3dc47.txt"

# Ensure destination folders exist
os.makedirs(DEST_IMAGES, exist_ok=True)
os.makedirs(DEST_LABELS, exist_ok=True)

# Get label basenames and sort them
label_basenames = sorted(
    os.path.splitext(f)[0]
    for f in os.listdir(SOURCE_LABELS)
    if f.endswith(".txt")
)

moved = 0
for name in label_basenames:
    label_file = name + ".txt"

    # Enforce cutoff
    if label_file > CUTOFF_FILENAME:
        break

    label_path = os.path.join(SOURCE_LABELS, label_file)
    if not os.path.exists(label_path):
        continue

    # Try to find matching image
    image_found = False
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        img_path = os.path.join(SOURCE_IMAGES, name + ext)
        if os.path.exists(img_path):
            shutil.copy2(img_path, os.path.join(DEST_IMAGES, name + ext))
            image_found = True
            break

    if image_found:
        shutil.copy2(label_path, os.path.join(DEST_LABELS, label_file))
        moved += 1

print(f"✅ Exported {moved} labeled image/label pairs to `yolo_dataset/train/`.")