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
    pillow_heif.register_heif_opener(thumbnails=True, thumbnails_autoload=False)
    # "images/hif/93FG5564.hif" - contains 1 image and two thumbnails for it.
    # "images/hif/93FG5559.hif" - contains 1 image and two thumbnails for it.
    # "images/nokia/collection/season_collection_1440x960.heic" - contains 4 images and 4 thumbnails.
    image_path = Path("images/hif/93FG5559.hif")
    try:
        img = Image.open(image_path)
        index = 1
        for frame in ImageSequence.Iterator(img):
            # `img.info["thumbnails"]` can be changed in future versions.
            for thumb in img.info["thumbnails"]:
                thumb.load()
                thumb_img = Image.frombytes(
                    thumb.mode,
                    thumb.size,
                    thumb.data,
                    "raw",
                    thumb.mode,
                    thumb.stride,
                )
                thumb_img.show(title=f"Img={index} Thumbnail={thumb.img_id}")
            img.show(title=f"Image index={index}")
            index += 1
    except Exception as e:
        print(f"{repr(e)} during processing {image_path.as_posix()}", file=sys.stderr)
        print(traceback.format_exc())
    exit(0)
