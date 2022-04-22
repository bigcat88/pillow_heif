import os
from pathlib import Path

from PIL import Image

import pillow_heif.HeifImagePlugin  # noqa

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
TARGET_FOLDER = "../converted"

# This demo converts jpeg to heic with low quality.
if __name__ == "__main__":
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    image_path = Path("images/rgb8_512_512_1_0.heic")
    append_image_path = Path("images/rgb8_512_512_1_2.heic")
    img = Image.open(image_path)
    append_img = Image.open(append_image_path)
    img.save(os.path.join(TARGET_FOLDER, "appended_pugs.heic"), save_all=True, append_images=[append_img])
    img.close()
