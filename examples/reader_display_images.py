import os
import sys
import traceback
from pathlib import Path

from PIL import Image

import pillow_heif

# This demo displays all thumbnails and all images.
if __name__ == "__main__":
    # Change directory to project root.
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
    # "images/hif/93FG5564.hif" - contains 1 image and two thumbnails for it.
    # "images/hif/93FG5559.hif" - contains 1 image and two thumbnails for it.
    # "images/nokia/collection/season_collection_1440x960.heic" - contains 4 images and 4 thumbnails.
    image_path = Path("images/nokia/collection/season_collection_1440x960.heic")
    pillow_heif.options().thumbnails = True
    pillow_heif.options().thumbnails_autoload = True
    try:
        if not pillow_heif.is_supported(image_path):
            raise ValueError("Unsupported image.")
        heif_image = pillow_heif.read_heif(image_path)
        print(f"number of images in file: {len(heif_image)}")
        for image in heif_image:
            for thumb in image.thumbnails:
                thumbnail_img = Image.frombytes(
                    thumb.mode,
                    thumb.size,
                    thumb.data,
                    "raw",
                    thumb.mode,
                    thumb.stride,
                )
                thumbnail_img.show(title=f"Thumbnail {thumb.img_id}")
            _img = Image.frombytes(
                image.mode,
                image.size,
                image.data,
                "raw",
                image.mode,
                image.stride,
            )
            _img.show(title=f"Image {image.info['img_id']}")
    except Exception as e:
        print(f"{repr(e)} during processing {image_path.as_posix()}", file=sys.stderr)
        print(traceback.format_exc())
    exit(0)
