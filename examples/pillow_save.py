import os
from pathlib import Path

from PIL import Image

import pillow_heif

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
TARGET_FOLDER = "../converted"

# This demo converts gif to heic.
if __name__ == "__main__":
    pillow_heif.register_heif_opener()
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    image_path = Path("images/non_heif/chi.gif")
    img = Image.open(image_path)
    img.save(os.path.join(TARGET_FOLDER, f"{image_path.stem}.heic"), quality=50, save_all=True)
    img.close()
