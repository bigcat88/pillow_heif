import os
import sys
import traceback
from pathlib import Path

import pillow_heif

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
    target_folder = "../converted"
    os.makedirs(target_folder, exist_ok=True)
    image_path = Path("images/pug_2_0.heic")
    try:
        heif_image = pillow_heif.open_heif(image_path)
        result_path = os.path.join(target_folder, f"{image_path.stem}.heic")
        del heif_image[1]
        heif_image.save(result_path, quality=35)
        heif_image.close()
    except Exception as e:
        print(f"{repr(e)} during processing {image_path.as_posix()}", file=sys.stderr)
        print(traceback.format_exc())
    exit(0)
