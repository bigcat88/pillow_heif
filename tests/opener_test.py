# import builtins
# import os
# from io import BytesIO
# from pathlib import Path
# from warnings import warn
#
# import pytest
# from PIL import Image, ImageCms, ImageSequence, UnidentifiedImageError
#
# from pillow_heif import HeifBrand, options, register_heif_opener
#
# register_heif_opener()
# os.chdir(os.path.dirname(os.path.abspath(__file__)))
#
# images_dataset = (
#     [f for f in list(Path().glob("images/nokia/*.heic"))]
#     + [f for f in list(Path().glob("images/avif/*.avif"))]  # noqa
#     + [f for f in list(Path().glob("images/*.avif"))]  # noqa
#     + [f for f in list(Path().glob("images/*.heic"))]  # noqa
#     + [f for f in list(Path().glob("images/*.hif"))]  # noqa
#     + [f for f in list(Path().glob("images/*.heif"))]  # noqa
# )
#
# if not options().avif:
#     warn("Skipping tests for `AV1` format due to lack of codecs.")
#     images_dataset = [e for e in images_dataset if not e.name.endswith(".avif")]
#
#
# # @pytest.mark.parametrize("img_info", heic_images[:4] + hif_images[:4] + avif_images[:4])
# # def test_load_images(img_info):
# #     with builtins.open(Path(img_info["file"]), "rb") as f:
# #         bytes_io = BytesIO(f.read())
# #     fh = builtins.open(Path(img_info["file"]), "rb")
# #     for _as in (Path(img_info["file"]).as_posix(), bytes_io, fh):
# #         pillow_image = Image.open(_as)
# #         assert getattr(pillow_image, "fp") is not None
# #         pillow_image.load()
# #         if img_info["images_count"] > 1:
# #             assert getattr(pillow_image, "fp") is not None
# #         else:
# #             assert getattr(pillow_image, "fp") is None
# #         pillow_image.load()
#
#
# # NEW TESTS
#
#
# @pytest.mark.parametrize("image_path", images_dataset)
# def test_open_images(image_path):
#     pillow_image = Image.open(image_path)
#     assert getattr(pillow_image, "fp") is not None
#     assert getattr(pillow_image, "heif_file") is not None
#     assert pillow_image.info
#     assert pillow_image.info["brand"] != HeifBrand.UNKNOWN.name
#
#     # if img_info["exif_length"] is not None:
#     #     assert len(pillow_image.info["exif"]) == img_info["exif_length"]
#     # else:
#     #     assert pillow_image.info["exif"] is None
#     # # If icc profile is present, it's size can be zero.
#     # if img_info.get("icc_profile", None) is None:
#     #     assert "icc_profile" not in pillow_image.info
#     # else:
#     #     assert len(pillow_image.info["icc_profile"]) == img_info["icc_profile"]
#     #     if len(pillow_image.info["icc_profile"]):
#     #         ImageCms.getOpenProfile(BytesIO(pillow_image.info["icc_profile"]))
#     # # If nclx profile is present, it's size can not be zero.
#     # if img_info.get("nclx_profile", None):
#     #     assert len(pillow_image.info["nclx_profile"]) == img_info["nclx_profile"]
#     # else:
#     #     assert "nclx_profile" not in pillow_image.info
#     # # Compare number of metadata records
#     # assert len(pillow_image.info["metadata"]) == len(img_info["metadata"])
#     # # Verify image
#     # pillow_image.verify()
#     # # Here we must check verify, but currently verify do nothing.
#     # # Check image iteration
#     # _last_img_id = -1
#     # for frame in ImageSequence.Iterator(pillow_image):
#     #     assert frame.info["img_id"] != _last_img_id
#     #     _last_img_id = frame.info["img_id"]
#
#
# @pytest.mark.parametrize("img_path", list(Path().glob("images/invalid/*")))
# def test_corrupted_open(img_path):
#     with pytest.raises(UnidentifiedImageError):
#         Image.open(img_path)
#     with pytest.raises(UnidentifiedImageError):
#         with open(img_path, "rb") as f:
#             Image.open(BytesIO(f.read()))
