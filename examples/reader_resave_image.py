import os
from pathlib import Path

import pillow_heif

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
TARGET_FOLDER = "../converted"

# Save from heic to new heic with lower quality.
if __name__ == "__main__":
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    image_path = Path("images/etc_heif/cat.hif")
    heif_file = pillow_heif.open_heif(image_path)
    result_path = os.path.join(TARGET_FOLDER, f"{image_path.stem}.heic")
    heif_file.save(result_path, quality=50)
