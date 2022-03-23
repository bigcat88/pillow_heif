import builtins
import hashlib
import os
import sys
import traceback
from json import dump
from pathlib import Path

import piexif
from PIL import Image, ImageFile, ImageSequence, UnidentifiedImageError

import pillow_heif


# This is not a real example, just file for development.
# We compare data from previous release to next, so here we generate data.
# So here are many code, that do nothing useful.
#
# Get all available info for current version about images in tests directory and dump it to images_info.json
#
# Function to dump info from Pillow.ImageFile
def _dump_info(result: dict, _img: ImageFile):
    # HEIF brand name.
    result["brand"] = pillow_heif.HeifBrand(_img.info["brand"]).name
    # For exif dump only type and data size.
    result["exif_length"] = len(_img.info["exif"]) if _img.info["exif"] else None
    if result["exif_length"]:
        _exif = piexif.load(_img.info["exif"])
        result["exif"] = {k: len(v) if v else None for k, v in _exif.items()}
    # For metadata dump only type and data size.
    result["metadata"] = {m["type"]: len(m["data"]) for m in _img.info["metadata"]}
    # For color profile dump only type and data size.
    if _img.info["color_profile"]:
        result["color_profile"] = _img.info["color_profile"]["type"]
        result["color_profile_length"] = len(_img.info["color_profile"]["data"])
    else:
        result["color_profile"] = None
    # icc_profile (color_profile is `prof` or `rICC`)
    icc_profile = _img.info.get("icc_profile", None)
    result["icc_profile"] = len(icc_profile) if icc_profile is not None else None
    # nclx_profile
    nclx_profile = _img.info.get("nclx_profile", None)
    result["nclx_profile"] = len(nclx_profile) if nclx_profile is not None else None
    result["dimensions"] = str(_img.size)
    all_top_lvl_images_count = 0
    top_lvl_images_info = []
    thumbnails_count = 0
    thumbnails_info = []
    for _img_frame in ImageSequence.Iterator(_img):
        all_top_lvl_images_count += 1
        top_lvl_images_info.append(str(_img_frame.heif_file))
        for _ in _img_frame.info["thumbnails"]:
            thumbnails_count += 1
            thumbnails_info.append(str(_))
    result["all_top_lvl_images_count"] = all_top_lvl_images_count
    result["all_top_lvl_images"] = top_lvl_images_info
    result["thumbnails_count"] = thumbnails_count
    result["thumbnails"] = thumbnails_info


if __name__ == "__main__":
    # Change directory to project root.
    os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
    pillow_heif.register_heif_opener(thumbnails=True, thumbnails_autoload=False)
    expected_data = []
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
            img_info = {
                "name": image_path.name,
                "file": image_path.as_posix(),
                "hash": _hash,
                "size": image_path.stat().st_size,
                "check_heif": pillow_heif.check_heif(image_path),
            }
            # Try to open it in strict mode first.
            pillow_heif.options().strict = True
            try:
                img = Image.open(image_path)
                img_info["strict"] = True
                img.close()
            except UnidentifiedImageError:
                # We fails open it in strict mode.
                img_info["strict"] = False
            # Now we know, can be the file opened in `strict` mode or not.
            pillow_heif.options().strict = img_info["strict"]
            img_info["supported"] = pillow_heif.is_supported(image_path)
            try:
                img = Image.open(image_path)
                img_info["valid"] = True
                img_info["mimetype"] = pillow_heif.get_file_mimetype(image_path)
                _dump_info(img_info, img)
                img_info["thumbnails_loaded"] = []
                img_info["all_top_lvl_images_loaded"] = []
                try:
                    img.load()
                    img_info["load"] = True
                    for __img_frame in ImageSequence.Iterator(img):
                        # if __img_frame.heif_file:
                        #     img_info["all_top_lvl_images_loaded"].append(str(__img_frame.heif_file))
                        # else:
                        #     img_info["all_top_lvl_images_loaded"].append("not implemented")
                        for _ in __img_frame.info["thumbnails"]:
                            img_info["thumbnails_loaded"].append(str(_))
                except pillow_heif.HeifError as e:
                    print(str(e))
                    img_info["load"] = False
            except UnidentifiedImageError:
                img_info["valid"] = False
            expected_data.append(img_info)
    except Exception as e:
        print(f"{repr(e)} during processing {image_path.as_posix()}", file=sys.stderr)
        print(traceback.format_exc())
    finally:
        with builtins.open("images_info.json", "w") as f:
            dump(expected_data, f, indent=2, skipkeys=True)
            print("", file=f)
