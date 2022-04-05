# import os
# from pathlib import Path
#
# from PIL import Image
#
# import pillow_heif
#
# # This demo creates `py_pug.heic` from `pug.jpeg`, `pug2.heic` and `pug3.heic` files.
# # This is temporary code, in next version there will be a much nicer API for that.
# # Currently `add_frombytes` does not get thumbnails saved, wait 0.2.2 version for easy API to do that.
# if __name__ == "__main__":
#     # Change directory to project root.
#     os.chdir(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests"))
#     target_folder = "../converted"
#     os.makedirs(target_folder, exist_ok=True)
#     # pillow_pug_jpeg = Image.open(Path("images/pug2.jpeg"))
#     # out_heif_container = pillow_heif.HeifFile().add_from_pillow(pillow_pug_jpeg)
#     out_heif_container = pillow_heif.open_heif(Path("images/pug2.heic"))
#     heif_file_to_add = pillow_heif.open_heif(Path("images/pug3.heic"))
#     out_heif_container.add_from_heif(heif_file_to_add)
#     out_heif_container[1].info["icc_profile"] = b""
#     out_heif_container.save(Path("../converted/pug2_0.heic"), thumb_ignore_mask=[0], thumb_boxes=[129], quality=40)
#     # out_heif_container.add_from_heif(heif_file_to_add[0])
#     exit(0)
#     color_prof = heif_file_to_add.info.get("nclx_profile", {})
#     if color_prof:
#         color_prof = {"nclx_profile": color_prof}
#     else:
#         color_prof = heif_file_to_add.info.get("icc_profile", {})
#         if color_prof:
#             color_prof = {"icc_profile_type": "prof", "icc_profile": color_prof}
#     additional_info = {"metadata": heif_file_to_add.info.get("metadata", [])}
#     additional_info.update(**color_prof)
#     out_heif_container.add_frombytes(
#         heif_file_to_add.mode,
#         heif_file_to_add.size,
#         heif_file_to_add.data,
#         heif_file_to_add.info["exif"],
#         additional_info,
#         heif_file_to_add.stride,
#     )
#     heif_file_to_add = pillow_heif.open_heif(Path("images/pug3.heic"))
#     # ---------
#     color_prof = heif_file_to_add.info.get("nclx_profile", {})
#     if color_prof:
#         color_prof = {"nclx_profile": color_prof}
#     else:
#         color_prof = heif_file_to_add.info.get("icc_profile", {})
#         if color_prof:
#             color_prof = {"icc_profile_type": "prof", "icc_profile": color_prof}
#     additional_info = {"metadata": heif_file_to_add.info.get("metadata", [])}
#     additional_info.update(**color_prof)
#     out_heif_container.add_frombytes(
#         heif_file_to_add.mode,
#         heif_file_to_add.size,
#         heif_file_to_add.data,
#         heif_file_to_add.info["exif"],
#         additional_info,
#         heif_file_to_add.stride,
#     )
#     out_heif_container.save(os.path.join(target_folder, "py_pug.heic"), quality=85, thumbnails=[100, 200, 300])
#     exit(0)
