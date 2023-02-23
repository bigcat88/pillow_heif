import os
from pathlib import Path

from PIL import Image

import pillow_heif.HeifImagePlugin  # noqa

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
TARGET_FOLDER = "../converted"

# Create HEIF file containing `RGB_8__29x100.png` and `RGBA_8__128x128.png`
if __name__ == "__main__":
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    image1_path = Path("images/non_heif/RGB_8__29x100.png")
    image2_path = Path("images/non_heif/RGBA_8__128x128.png")
    img1 = Image.open(image1_path)
    img2 = Image.open(image2_path)
    result_path = os.path.join(TARGET_FOLDER, "RGB_A_8.heic")
    img1.save(result_path, quality=35, save_all=True, append_images=[img2])
