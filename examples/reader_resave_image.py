import os
from pathlib import Path

import pillow_heif

# Save from heic to new heic with lower quality.
if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
    target_folder = "../converted"
    os.makedirs(target_folder, exist_ok=True)
    image_path = Path("images/cat.hif")
    heif_file = pillow_heif.open_heif(image_path)
    result_path = os.path.join(target_folder, f"{image_path.stem}.heic")
    heif_file.save(result_path, quality=50)
    heif_file.close()
