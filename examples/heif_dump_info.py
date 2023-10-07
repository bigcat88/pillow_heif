from io import BytesIO

import piexif
from PIL import ImageCms

import pillow_heif

if __name__ == "__main__":
    file = "../tests/images/heif_other/cat.hif"  # noqa
    print("Dumping info for file:", file)
    print("Supported:", pillow_heif.is_supported(file))
    print("Mime:", pillow_heif.get_file_mimetype(file))
    heif_file = pillow_heif.open_heif(file, convert_hdr_to_8bit=False)
    print("Number of images:", len(heif_file))
    print("Information about each image:")
    for image in heif_file:
        print("\tMode:", image.mode)
        print("\tDepth:", image.info["bit_depth"])
        print("\tAlpha:", image.has_alpha)
        print("\tSize:", image.size)
        print("\tData size:", len(image.data))
        print("\tStride:", image.stride)
        print("\tThumbnails:", list(image.info["thumbnails"]))
        if image.info.get("icc_profile", None) is not None:
            if len(image.info["icc_profile"]):
                icc_profile = BytesIO(image.info["icc_profile"])
                print("\tICC:", str(ImageCms.getProfileDescription(icc_profile)).strip())
            else:
                print("\tICC: Empty")
        if image.info.get("nclx_profile", None):
            print("\tNCLX:", image.info["nclx_profile"])
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
            print(f"\tXmp size: {len(image.info['xmp'])}")
        if image.info.get("metadata", None):
            print("\tMetadata:")
            for block in image.info["metadata"]:
                print("\t\tType:", block["type"])
                print("\t\tcontent_type:", block["content_type"])
                print("\t\tData length:", len(block["data"]))
        print()
