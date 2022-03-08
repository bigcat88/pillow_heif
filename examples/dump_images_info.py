import sys
import os
import builtins
import traceback
from pathlib import Path
from json import dump
import hashlib

from PIL import Image, UnidentifiedImageError
import piexif
import pillow_heif


# This is not a real example, just file for development.
# So here are many code, that do nothing useful.
#
# Get all available info for current version about images in tests directory and dump it to images_info.json
if __name__ == "__main__":
    # Change directory to project root.
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
    pillow_heif.register_heif_opener()
    expected_data = {}
    image_path = Path(".")
    try:
        for image_path in list(Path().glob("images/**/*.*")):
            if image_path.name in (".DS_Store", "README.txt", "LICENSE.txt"):
                continue
            # Calculate file md5, it will be the key in dictionary for that file info.
            with builtins.open(image_path, "rb") as _:
                md5 = hashlib.md5()
                md5.update(_.read())
                _hash = md5.hexdigest()
            img_info = {"file": image_path.as_posix(), "name": image_path.name, "size": image_path.stat().st_size}
            # Try to open it in strict mode first.
            pillow_heif.get_cfg_options()["strict"] = True
            try:
                img = Image.open(image_path)
                img_info["strict"] = True
                img.close()
            except UnidentifiedImageError:
                # We fails open it in strict mode.
                img_info["strict"] = False
            # Now we know, can be the file opened in `strict` mode or not.
            pillow_heif.get_cfg_options()["strict"] = img_info["strict"]
            img = Image.open(image_path)
            # HEIF brand name.
            img_info["brand"] = pillow_heif.HeifBrand(img.info["brand"]).name
            # For exif dump only type and data size.
            img_info["exif_length"] = len(img.info["exif"]) if img.info["exif"] else None
            if img_info["exif_length"]:
                _exif = piexif.load(img.info["exif"])
                img_info["exif"] = {k: len(v) if v else None for k, v in _exif.items()}
            # For metadata dump only type and data size.
            img_info["metadata"] = {e["type"]: len(e["data"]) for e in img.info["metadata"]}
            # For color profile dump only type and data size.
            if img.info["color_profile"]:
                img_info["color_profile"] = img.info["color_profile"]["type"]
                img_info["color_profile_length"] = len(img.info["color_profile"]["data"])
            else:
                img_info["color_profile"] = None
            # icc_profile
            icc_profile = img.info.get("icc_profile", None)
            img_info["icc_profile"] = len(icc_profile) if icc_profile else None
            # nclx_profile
            nclx_profile = img.info.get("nclx_profile", None)
            img_info["nclx_profile"] = len(nclx_profile) if nclx_profile else None
            expected_data[_hash] = img_info
    except Exception as e:
        print(f"{repr(e)} during processing {image_path.as_posix()}", file=sys.stderr)
        print(traceback.format_exc())
    finally:
        with builtins.open("images_info.json", "w") as f:
            dump(expected_data, f, indent=2, skipkeys=True)
