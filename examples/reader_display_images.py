import os
from pathlib import Path

import pillow_heif

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))

# This demo displays all thumbnails and all images.
if __name__ == "__main__":
    image_path = Path("images/etc_heif/nokia/alpha_3_2.heic")
    heif_image = pillow_heif.open_heif(image_path)
    print(f"number of images in file: {len(heif_image)}")
    for image in heif_image:
        for thumb in image.thumbnails:
            thumbnail_img = thumb.to_pillow()
            thumbnail_img.show(title=f"Thumbnail {thumb.info['thumb_id']}")
        _img = image.to_pillow()
        _img.show(title=f"Image {image.info['img_id']}")
