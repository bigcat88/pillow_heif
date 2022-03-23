import os
import sys
import traceback
from pathlib import Path

from PIL import Image

import pillow_heif

# This demo convert images and thumbnails from heic file to jpeg image(s).
if __name__ == "__main__":
    # Change directory to project root.
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
    target_folder = "../converted"
    os.makedirs(target_folder, exist_ok=True)
    pillow_heif.options().update(thumbnails=True, thumbnails_autoload=True)
    # "images/hif/93FG5564.hif" - contains 1 image and two thumbnails for it.
    # "images/hif/93FG5559.hif" - contains 1 image and two thumbnails for it.
    # "images/nokia/collection/season_collection_1440x960.heic" - contains 4 images and 4 thumbnails.
    image_path = Path("images/hif/93FG5564.hif")
    try:
        if not pillow_heif.is_supported(image_path):
            raise ValueError("Unsupported image.")
        heif_image = pillow_heif.read_heif(image_path)
        print(f"number of images in file: {len(heif_image)}")
        for image in heif_image:
            for thumb in image.thumbnails:
                thumb_img = Image.frombytes(
                    thumb.mode,
                    thumb.size,
                    thumb.data,
                    "raw",
                    thumb.mode,
                    thumb.stride,
                )
                result_path = os.path.join(target_folder, f"thumb_{thumb.img_id}_{image_path.stem}.png")
                thumb_img.save(result_path)
            _img = Image.frombytes(
                image.mode,
                image.size,
                image.data,
                "raw",
                image.mode,
                image.stride,
            )
            result_path = os.path.join(target_folder, f"img_{image.info['img_id']}_{image_path.stem}.png")
            _img.save(result_path)
    except Exception as e:
        print(f"{repr(e)} during processing {image_path.as_posix()}", file=sys.stderr)
        print(traceback.format_exc())
    exit(0)
