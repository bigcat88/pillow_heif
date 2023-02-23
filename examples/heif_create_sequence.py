import os
from pathlib import Path

from PIL import Image

import pillow_heif

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
TARGET_FOLDER = "../converted"

# Create HEIF file containing `RGB_8__29x100.png` and `RGBA_8__128x128.png`
if __name__ == "__main__":
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    img1 = Image.open(Path("images/non_heif/RGB_8__29x100.png"))
    img2 = Image.open(Path("images/non_heif/RGBA_8__128x128.png"))
    result_path = os.path.join(TARGET_FOLDER, "RGB_A_8.heic")
    heif_file = pillow_heif.from_pillow(img1)
    heif_file.add_from_pillow(img2)  # it can be replaced with `append_images` parameter.
    heif_file.save(result_path, quality=35)
