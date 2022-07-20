import os
from pathlib import Path

import pillow_heif

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
TARGET_FOLDER = "../converted"

# zPug_3 contains three images, we remove first image
if __name__ == "__main__":
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    image_path = Path("images/heif/zPug_3.heic")
    heif_image = pillow_heif.open_heif(image_path)
    result_path = os.path.join(TARGET_FOLDER, f"{image_path.stem}.heic")
    del heif_image[0]
    heif_image.save(result_path, quality=35)
