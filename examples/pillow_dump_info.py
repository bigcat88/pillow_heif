import sys
from io import BytesIO

import piexif
from PIL import Image, ImageCms, ImageSequence

import pillow_heif.HeifImagePlugin

if __name__ == "__main__":
    file = sys.argv[1]
    print("Dumping info for file:", file)
    heif_pillow = Image.open(file)
    print("Number of images:", len([i for i in ImageSequence.Iterator(heif_pillow)]))
    print("Information about each image:")
    for image in ImageSequence.Iterator(heif_pillow):
        print("Number of thumbnails:", len(image.info["thumbnails"]))
        print("\tMode:", image.mode)
        print("\tSize:", image.size)
        print("\tData size:", len(image.tobytes()))
        if image.info.get("icc_profile", None) is not None:
            if len(image.info["icc_profile"]):
                icc_profile = BytesIO(image.info["icc_profile"])
                print("\tICC:", str(ImageCms.getProfileDescription(icc_profile)).strip())
            else:
                print("\tICC: Empty")
        if image.info.get("nclx_profile", None):
            print("\tNCLX:", "TODO")
        if image.info.get("exif", None):
            print("\tExif:")
            exif_dict = piexif.load(image.info["exif"], key_is_name=True)
            for key, value in exif_dict.items():
                print(f"\t\t{key}:")
                if value is not None:
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, bytes) and len(sub_value) > 20:
                            print(f"\t\t\t{sub_key}: {len(sub_value)} bytes.")
                        else:
                            print(f"\t\t\t{sub_key}: {sub_value}")
        if image.info.get("xmp", None):
            print("\tXmp:")
            print("\t\t", pillow_heif.getxmp(image.info["xmp"]))
        if image.info.get("metadata", None):
            print("\tMetadata:")
            for block in image.info["metadata"]:
                print("\t\tType:", block["type"])
                print("\t\tcontent_type:", block["content_type"])
                print("\t\tData length:", len(block["data"]))
        print("\tThumbnails:")
        for thumbnail in image.info["thumbnails"]:
            print("\t\tMode:", thumbnail.mode)
            print("\t\tSize:", thumbnail.size)
            print("\t\tData size:", len(thumbnail.data))
            print("")
        print("")
