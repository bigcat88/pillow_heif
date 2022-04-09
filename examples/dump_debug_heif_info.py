import sys

import pillow_heif

if __name__ == "__main__":
    file = sys.argv[1]
    print("Dumping info for file:", file)
    print("Check result:", pillow_heif.HeifFiletype(pillow_heif.check_heif(file)))
    print("Supported:", pillow_heif.is_supported(file))
    print("Mime:", pillow_heif.get_file_mimetype(file))
    heif_file = pillow_heif.open_heif(file, convert_hdr_to_8bit=False)
    # # Uncomment this if you need `boxes` from heif header.
    # from pathlib import Path
    # boxes_name = Path(file).stem + ".txt"
    # print(f"Saving debug boxes to {boxes_name}")
    # heif_file._debug_dump(boxes_name)  # noqa
    print("Number of images:", len(heif_file))
    print("Number of thumbnails:", len([i for i in heif_file.thumbnails_all()]))
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
            print("\tICC:", "TODO")
        elif image.info.get("nclx_profile", None):
            print("\tNCLX:", "TODO")
        if image.info.get("exif", None):
            print("\tExif:", "TODO")
        if image.info.get("metadata", None):
            print("\tMetadata:", "TODO")
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
