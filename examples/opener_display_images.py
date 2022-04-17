import os
import sys
import traceback
from pathlib import Path

from PIL import Image, ImageSequence

import pillow_heif

# This demo displays all thumbnails and all images from file.
if __name__ == "__main__":
    # Change directory to project root.
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
    pillow_heif.register_heif_opener()
    image_path = Path("images/pug_1_1.heic")
    try:
        img = Image.open(image_path)
        img.load()
        for i, frame in enumerate(ImageSequence.Iterator(img)):
            for thumb in img.info["thumbnails"]:
                thumb_img = thumb.to_pillow()
                thumb_img.show(title=f"Img={i} Thumbnail={thumb.info['thumb_id']}")
            img.show(title=f"Image index={i}")
    except Exception as e:
        print(f"{repr(e)} during processing {image_path.as_posix()}", file=sys.stderr)
        print(traceback.format_exc())
    exit(0)
