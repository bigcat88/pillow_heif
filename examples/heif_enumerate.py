import os
from pathlib import Path

import pillow_heif

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))

# This demo displays all images in a file.
if __name__ == "__main__":
    image_path = Path("images/heif_other/nokia/alpha.heic")
    heif_image = pillow_heif.open_heif(image_path)
    print(f"number of images in file: {len(heif_image)}")
    for i, image in enumerate(heif_image):
        _img = image.to_pillow()
        _img.show(title=f"Image index={i}")
