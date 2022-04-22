import os
from pathlib import Path

from PIL import Image

import pillow_heif

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
TARGET_FOLDER = "../converted"

if __name__ == "__main__":
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    image_path = Path("images/jpeg_gif_png/chi.gif")
    pillow_image = Image.open(image_path)
    heif_image = pillow_heif.from_pillow(pillow_image)
    result_path = os.path.join(TARGET_FOLDER, f"{image_path.stem}.heic")
    heif_image.save(result_path, quality=35)
