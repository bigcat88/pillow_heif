import os
from pathlib import Path

from PIL import Image

import pillow_heif

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
TARGET_FOLDER = "../converted"

# Create HEIF file containing `RGB_16.png` and `RGBA_16.png`
if __name__ == "__main__":
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    image1_path = Path("images/non_heif/RGB_16.png")
    image2_path = Path("images/non_heif/RGBA_16.png")
    img1 = Image.open(image1_path)
    img2 = Image.open(image2_path)
    result_path = os.path.join(TARGET_FOLDER, "RGB_A_8.heic")
    heif_file = pillow_heif.from_pillow(img1)
    heif_file.add_from_pillow(img2)  # it can be replaced with `append_images` parameter.
    heif_file.save(result_path, quality=35)
