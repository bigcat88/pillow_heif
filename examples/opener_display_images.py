import os
import sys
import traceback
from pathlib import Path

from PIL import Image

import pillow_heif

# This demo displays all thumbnails and first main image.
if __name__ == "__main__":
    # Change directory to project root.
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
    pillow_heif.register_heif_opener(thumbnails=True, thumbnails_autoload=False)
    # "images/hif/93FG5564.hif" - contains 1 image and two thumbnails for it.
    image_path = Path("images/hif/93FG5564.hif")
    try:
        img = Image.open(image_path)
        img.load()
        # `img.info["thumbnails"]` can be changed in future versions.
        for thumb in img.info["thumbnails"]:
            thumbnail_img = Image.frombytes(
                thumb.mode,
                thumb.size,
                thumb.data,
                "raw",
                thumb.mode,
                thumb.stride,
            )
            thumbnail_img.show(title=f"Thumbnail {id}")
        # This is a temporary workaround. Standard says that app must ignore EXIF orientation, if `irot` present.
        img.info["exif"] = None
        img.show(title="Main")
    except Exception as e:
        print(f"{repr(e)} during processing {image_path.as_posix()}", file=sys.stderr)
        print(traceback.format_exc())
    exit(0)
