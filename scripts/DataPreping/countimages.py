import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
labels_path = os.path.join(PROJECT_ROOT, "data", "training", "labels")

cutoff = "2424_signer3_32ea09cdbe50462a0e27038046e3dc47.txt"

total_boxes = 0
files = 0
no_sig = 0
multi_sig = 0
single_sig = 0

# Sort the label filenames for consistent order
for filename in sorted(os.listdir(labels_path)):
    if not filename.endswith(".txt"):
        continue

    if filename > cutoff:
        break  # Stop after the last reviewed image

    with open(os.path.join(labels_path, filename), "r") as f:
        lines = [line.strip() for line in f if line.strip()]
        box_count = len(lines)
        total_boxes += box_count
        files += 1

        if box_count == 0:
            no_sig += 1
        elif box_count == 1:
            single_sig += 1
        else:
            multi_sig += 1

print(f"📦 Labeled images (up to cutoff): {files}")
print(f"✍️ Total autograph boxes: {total_boxes}")
print(f"➗ Average boxes per image: {total_boxes / files:.2f}")
print(f"🚫 Images with no sigs: {no_sig}")
print(f"✔️ Images with single sig: {single_sig}")
print(f"📚 Images with multiple sigs: {multi_sig}")
