import os
import sys
import traceback
from pathlib import Path

import pillow_heif

# This demo displays all thumbnails and all images.
if __name__ == "__main__":
    # Change directory to project root.
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
    image_path = Path("images/nokia/alpha.heic")
    try:
        if not pillow_heif.is_supported(image_path):
            raise ValueError("Unsupported image.")
        heif_image = pillow_heif.open_heif(image_path)
        print(f"number of images in file: {len(heif_image)}")
        for image in heif_image:
            for thumb in image.thumbnails:
                thumbnail_img = thumb.to_pillow()
                thumbnail_img.show(title=f"Thumbnail {thumb.info['thumb_id']}")
            _img = image.to_pillow()
            _img.show(title=f"Image {image.info['img_id']}")
    except Exception as e:
        print(f"{repr(e)} during processing {image_path.as_posix()}", file=sys.stderr)
        print(traceback.format_exc())
    exit(0)
