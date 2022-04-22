import os
from pathlib import Path

from PIL import Image

import pillow_heif

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
TARGET_FOLDER = "../converted"

# This demo creates `three_images.heic` from `rgba10bit.png`, `rgb8_512_512_1_0.heic` and `rgb8_512_512_1_2.heic`.
if __name__ == "__main__":
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    pillow_pug_jpeg = Image.open(Path("images/jpeg_gif_png/rgba10bit.png"))
    out_heif_container = pillow_heif.from_pillow(pillow_pug_jpeg)
    out_heif_container.add_from_heif(pillow_heif.open_heif(Path("images/rgb8_512_512_1_0.heic")))
    out_heif_container.add_from_heif(pillow_heif.open_heif(Path("images/rgb8_512_512_1_2.heic")))
    out_heif_container.save(Path("../converted/three_images.heic"), quality=90)
