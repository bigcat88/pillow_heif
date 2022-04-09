import os
from pathlib import Path

from PIL import Image

import pillow_heif

# This demo creates `py_pug.heic` from `pug.jpeg`, `pug2.heic` and `pug3.heic` files.
if __name__ == "__main__":
    # Change directory to project root.
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
    target_folder = "../converted"
    os.makedirs(target_folder, exist_ok=True)
    pillow_pug_jpeg = Image.open(Path("images/jpeg_gif_png/pug.jpeg"))
    out_heif_container = pillow_heif.from_pillow(pillow_pug_jpeg)
    out_heif_container.add_from_heif(pillow_heif.open_heif(Path("images/pug_1_0.heic")))
    out_heif_container.add_from_heif(pillow_heif.open_heif(Path("images/pug_1_2.heic")))
    out_heif_container.save(Path("../converted/py_pug.heic"), quality=90)
    exit(0)
