from io import BytesIO

from PIL import Image, ImageCms, ImageSequence
from PIL.ExifTags import TAGS

import pillow_heif.HeifImagePlugin  # noqa

if __name__ == "__main__":
    file = "../tests/images/heif_other/cat.hif"
    print("Dumping info for file:", file)
    heif_pillow = Image.open(file)
    print("Number of images:", len(list(ImageSequence.Iterator(heif_pillow))))
    print("Information about each image:")
    for image in ImageSequence.Iterator(heif_pillow):
        print("\tMode:", image.mode)
        print("\tSize:", image.size)
        print("\tThumbnails:", list(image.info["thumbnails"]))
        print("\tData size:", len(image.tobytes()))
        if image.info.get("icc_profile", None) is not None:
            if len(image.info["icc_profile"]):
                icc_profile = BytesIO(image.info["icc_profile"])
                print("\tICC:", str(ImageCms.getProfileDescription(icc_profile)).strip())
            else:
                print("\tICC: Empty")
        if image.info.get("nclx_profile", None):
            print("\tNCLX:", image.info["nclx_profile"])
        exif = image.getexif()
        if exif:
            exif = exif._get_merged_dict()  # noqa
        for k, v in exif.items():
            if isinstance(v, bytes) and len(v) > 8:
                print(f"{TAGS[k]} : size {len(v)} bytes")
            else:
                print(TAGS[k], ":", v)
        xmp = image.getxmp()
        if xmp:
            print("\tXmp:")
            print("\t\t", xmp)
        if image.info.get("metadata", None):
            print("\tMetadata:")
            for block in image.info["metadata"]:
                print("\t\tType:", block["type"])
                print("\t\tcontent_type:", block["content_type"])
                print("\t\tData length:", len(block["data"]))
        print()
