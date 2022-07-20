import os
from pathlib import Path

from PIL import Image, ImageSequence

import pillow_heif

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))

# This demo displays all thumbnails and all images from file.
if __name__ == "__main__":
    pillow_heif.register_heif_opener()
    image_path = Path("images/heif_other/nokia/alpha.heic")
    img = Image.open(image_path)
    for i, frame in enumerate(ImageSequence.Iterator(img)):
        for thumb in img.info["thumbnails"]:
            thumb_img = thumb.to_pillow()
            thumb_img.show(title=f"Thumbnail for img={i}")
        img.show(title=f"Image index={i}")
