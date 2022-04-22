import sys
from io import BytesIO

import piexif
from PIL import ImageCms

import pillow_heif

if __name__ == "__main__":
    file = sys.argv[1]
    # file = "../tests/images/rgb8_128_128_2_1.heic"
    print("Dumping info for file:", file)
    print("Check result:", pillow_heif.HeifFiletype(pillow_heif.check_heif(file)))
    print("Supported:", pillow_heif.is_supported(file))
    print("Mime:", pillow_heif.get_file_mimetype(file))
    heif_file = pillow_heif.open_heif(file, convert_hdr_to_8bit=False)
    print("Number of images:", len(heif_file))
    print("Number of thumbnails:", len(list(heif_file.thumbnails_all())))
    print("Information about each image:")
    for image in heif_file:
        print("\tID:", image.info["img_id"])
        print("\tDepth:", image.bit_depth)
        print("\tMode:", image.mode)
        print("\tAlpha:", image.has_alpha)
        print("\tSize:", image.size)
        __imagine_stride = image.size[0] * 3 if image.mode == "RGB" else image.size[0] * 4
        if image.bit_depth > 8:
            __imagine_stride *= 2
        print("\tImaginable Stride:", __imagine_stride)
        print("\tReal Stride:", image.stride)
        print("\tChroma:", image.chroma)
        print("\tColor:", image.color)
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
        for thumbnail in image.thumbnails:
            print("\t\tID:", thumbnail.info["thumb_id"])
            print("\t\tFor image with index:", thumbnail.info["img_index"])
            print("\t\tDepth:", thumbnail.bit_depth)
            print("\t\tMode:", thumbnail.mode)
            print("\t\tAlpha:", thumbnail.has_alpha)
            print("\t\tSize:", thumbnail.size)
            __imagine_stride = thumbnail.size[0] * 3 if thumbnail.mode == "RGB" else thumbnail.size[0] * 4
            if thumbnail.bit_depth > 8:
                __imagine_stride *= 2
            print("\t\tImaginable Stride:", __imagine_stride)
            print("\t\tReal Stride:", thumbnail.stride)
            print("\t\tChroma:", thumbnail.chroma)
            print("\t\tColor:", thumbnail.color)
            print("")
        print("")
