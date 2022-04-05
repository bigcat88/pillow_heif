import os
from pathlib import Path

import pillow_heif

# Save from heic to new heic with lower quality.
if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
    target_folder = "../converted"
    os.makedirs(target_folder, exist_ok=True)
    image_path = Path("images/nokia/overlay/overlay_1000x680.heic")
    heif_file = pillow_heif.open_heif(image_path, convert_hdr_to_8bit=False)  # to_8bit=False for `.hif` files.
    result_path = os.path.join(target_folder, f"{image_path.stem}.heic")
    heif_file.save(result_path, quality=100)
    heif_file.close()
