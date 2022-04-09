import os
import sys
import traceback
from pathlib import Path

from PIL import Image

import pillow_heif

# This demo converts jpeg to heic with low quality.
if __name__ == "__main__":
    # Change directory to project root.
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
    pillow_heif.register_heif_opener()
    target_folder = "../converted"
    os.makedirs(target_folder, exist_ok=True)
    image_path = Path("images/jpeg_gif_png/pug.jpeg")
    try:
        img = Image.open(image_path)
        img.save(os.path.join(target_folder, f"{image_path.stem}.heic"), quality=50)
        img.close()
    except Exception as e:
        print(f"{repr(e)} during processing {image_path.as_posix()}", file=sys.stderr)
        print(traceback.format_exc())
    exit(0)
