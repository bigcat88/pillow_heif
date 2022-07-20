import os
from pathlib import Path

import pillow_heif

os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
TARGET_FOLDER = "../converted"

# Save from heic to new heic with lower quality.
if __name__ == "__main__":
    os.makedirs(TARGET_FOLDER, exist_ok=True)
    image_path = Path("images/heif_other/cat.hif")
    # cat.hif is a 10 bit image, it will be saved as 8 bit.
    # change convert_hdr_to_8bit to False to save it in original depth.
    heif_file = pillow_heif.open_heif(image_path, convert_hdr_to_8bit=True)
    result_path = os.path.join(TARGET_FOLDER, f"{image_path.stem}.heic")
    heif_file.save(result_path, quality=50)
