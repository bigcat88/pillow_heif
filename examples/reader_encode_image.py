# import os
# import sys
# import traceback
# from pathlib import Path
#
# from PIL import Image
#
# import pillow_heif
#
# if __name__ == "__main__":
#     os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
#     nclx_heif = pillow_heif.open_heif("images/nclx.hif", convert_hdr_to_8bit=False)
#     aaa = pillow_heif.open_heif("images/pug_2_2.heic", convert_hdr_to_8bit=False)
#     # aaa.scale(24, 10)
#     # aaa.scale(639, 480)
#     thumbs = aaa.get_img_thumb_mask_for_save(pillow_heif.HeifSaveMask.SAVE_ALL, thumb_box=0)
#     aaa.add_thumbs_to_mask(thumbs, [511])
#     aaa[0].info.pop("icc_profile")
#     aaa[0].info.pop("icc_profile_type")
#     aaa[1].info.pop("icc_profile")
#     aaa[1].info.pop("icc_profile_type")
#     aaa[0].info["nclx_profile"] = nclx_heif.info["nclx_profile"]
#     aaa[1].info["nclx_profile"] = nclx_heif.info["nclx_profile"]
#     aaa.save("images/pug_2_3.heic", quality=36, save_mask=thumbs)
#     exit(0)
#
#     target_folder = "../converted"
#     os.makedirs(target_folder, exist_ok=True)
#     # image_path = Path("images/jpeg_gif_png/pug.jpeg")
#     image_path = Path("images/nokia/alpha.heic")
#     try:
#         # pillow_image = Image.open(image_path)
#         # heif_image = pillow_heif.HeifFile().add_from_pillow(pillow_image)
#         heif_image = pillow_heif.open_heif(image_path)
#         result_path = os.path.join(target_folder, f"{image_path.stem}_.heic")
#         heif_image.save(result_path, quality=35, thumb_boxes=[211])
#         heif_image.close()
#     except Exception as e:
#         print(f"{repr(e)} during processing {image_path.as_posix()}", file=sys.stderr)
#         print(traceback.format_exc())
#     exit(0)
