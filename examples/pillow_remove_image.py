import os
from pathlib import Path

from PIL import Image, ImageSequence

import pillow_heif.HeifImagePlugin  # noqa

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
TARGET_FOLDER = "../converted"

# rgb8_128_128_2_1 contains two images, we remove first image
if __name__ == "__main__":
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    image_path = Path("images/rgb8_128_128_2_1.heic")
    pillow_img = Image.open(image_path)
    result_path = os.path.join(TARGET_FOLDER, f"{image_path.stem}.heic")
    frames = []
    for frame in ImageSequence.Iterator(pillow_img):
        frames.append(frame.copy())
    del frames[0]
    frames[0].save(result_path, save_all=True, quality=35, append_images=frames[1:])
