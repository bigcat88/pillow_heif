import os
from pathlib import Path

from PIL import Image, ImageSequence

import pillow_heif

pillow_heif.register_heif_opener()

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
TARGET_FOLDER = "../converted"

if __name__ == "__main__":
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    image_path = Path("images/heif_other/nokia/alpha.heic")
    im = Image.open(image_path)
    result_path = os.path.join(TARGET_FOLDER, f"{image_path.stem}.heic")
    for frame in ImageSequence.Iterator(im):
        pillow_heif.add_thumbnails(frame, [256, 372])
    im.save(result_path, quality=35, save_all=True)

    # Next code will remove thumbnails
    im = Image.open(result_path)
    del im.info["thumbnails"][0]  # remove first thumbnail
    del im.info["thumbnails"][0]  # remove second thumbnail
    result_path = os.path.join(TARGET_FOLDER, f"{image_path.stem}_no_thumbs.heic")
    im.save(result_path, quality=35, save_all=True)
