import os
import sys
import traceback
from pathlib import Path

from PIL import Image

import pillow_heif.HeifImagePlugin  # noqa

# This demo converts jpeg to heic with low quality.
if __name__ == "__main__":
    # Change directory to project root.
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
    target_folder = "../converted"
    os.makedirs(target_folder, exist_ok=True)
    image_path = Path("images/rgb8_512_512_1_0.heic")
    append_image_path = Path("images/rgb8_512_512_1_2.heic")
    try:
        img = Image.open(image_path)
        append_img = Image.open(append_image_path)
        img.save(os.path.join(target_folder, "appended_pugs.heic"), save_all=True, append_images=[append_img])
        img.close()
    except Exception as e:
        print(f"{repr(e)} during processing {image_path.as_posix()}", file=sys.stderr)
        print(traceback.format_exc())
    exit(0)
