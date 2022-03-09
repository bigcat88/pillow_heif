import os
import builtins

# from gc import collect
from io import BytesIO
from pathlib import Path
from json import load

import pytest

# from PIL import Image, ImageCms
from pillow_heif import open_heif, read_heif, HeifFile, UndecodedHeifFile, HeifError, libheif_version


os.chdir(os.path.dirname(os.path.abspath(__file__)))
with builtins.open("images_info.json", "rb") as _:
    all_images = load(_)
invalid_images = [e for e in all_images if not e["valid"]]
heif_images = [e for e in all_images if e["valid"]]

heic_images = [e for e in heif_images if e["name"].endswith(".heic")]
hif_images = [e for e in heif_images if e["name"].endswith(".hif")]
avif_images = [e for e in heif_images if e["name"].endswith(".avif")]


# @pytest.mark.parametrize("path", heif_files)
# def test_check(path):
#     filetype = pillow_heif.check_heif(path)
#     assert pillow_heif.heif_filetype_no != filetype
#     unsupported_list = [
#         "rally_burst.heic",
#         "bird_burst.heic",
#         "starfield_animation.heic",
#         "sea1_animation.heic",
#     ]
#     if os.path.basename(path) in unsupported_list:
#         assert pillow_heif.heif_filetype_yes_unsupported == filetype
#     else:
#         assert pillow_heif.heif_filetype_yes_unsupported != filetype
#
#
# @pytest.mark.parametrize("path", heif_files[:2])
# def test_get_bytes_from_path(path):
#     d = pillow_heif.reader._get_bytes(path)
#     assert d == path.read_bytes()
#
#
# @pytest.mark.parametrize("path", heif_files[:2])
# def test_get_bytes_from_file_name(path):
#     d = pillow_heif.reader._get_bytes(str(path))
#     assert d == path.read_bytes()
#
#
# @pytest.mark.parametrize("path", heif_files[:2])
# def test_get_bytes_from_file_object(path):
#     with open(path, "rb") as f:
#         d = pillow_heif.reader._get_bytes(f)
#     assert d == path.read_bytes()
#
#
# @pytest.mark.parametrize("path", heif_files[:2])
# def test_get_bytes_from_bytes(path):
#     with open(path, "rb") as f:
#         d = pillow_heif.reader._get_bytes(f.read())
#     assert d == path.read_bytes()
#
#
# @pytest.fixture(scope="session", params=heif_files)
# def heif_file(request):
#     return pillow_heif.read_heif(request.param)
#
#
# @pytest.mark.parametrize("path", heif_files)
# def test_open_and_load(path):
#     heif_file = pillow_heif.open_heif(path)
#     assert heif_file.size[0] > 0
#     assert heif_file.size[1] > 0
#     assert heif_file.has_alpha is not None
#     assert heif_file.mode is not None
#     assert heif_file.bit_depth is not None
#
#     assert heif_file.data is None
#     assert heif_file.stride is None
#
#     if path.name == "arrow__prof.heic":
#         assert heif_file.metadata
#         assert heif_file.color_profile
#
#     res = heif_file.load()
#     assert heif_file is res
#     assert heif_file.data is not None
#     assert heif_file.stride is not None
#     assert len(heif_file.data) >= heif_file.stride * heif_file.size[1]
#     assert type(heif_file.data[:100]) == bytes
#     assert str(heif_file).find("HeifFile") != -1
#
#     # Subsequent calls don't change anything
#     res = heif_file.load()
#     assert heif_file is res
#     assert heif_file.data is not None
#     assert heif_file.stride is not None
#     heif_file.close()
#
#
# @pytest.mark.parametrize("path", heif_files)
# def test_open_and_load_data_not_collected(path):
#     data = path.read_bytes()
#     heif_file = pillow_heif.open_heif(data)
#     data = None  # heif_file.load() should work even if there is no other refs to the source data.
#     collect()
#     heif_file.load()
#
#
# def to_pillow_image(heif_file):
#     return Image.frombytes(
#         heif_file.mode,
#         heif_file.size,
#         heif_file.data,
#         "raw",
#         heif_file.mode,
#         heif_file.stride,
#     )
#
#
# @pytest.mark.parametrize("path", heic_files)
# def test_read_bytes(path):
#     with open(path, "rb") as f:
#         d = f.read()
#         heif_file = pillow_heif.read_heif(d)
#         assert heif_file is not None
#         width, height = heif_file.size
#         assert width > 0
#         assert height > 0
#         assert heif_file.brand != pillow_heif.constants.heif_brand_unknown_brand
#         assert len(heif_file.data) > 0
#
#
# @pytest.mark.parametrize("path", heic_files[:2])
# def test_read_bytearrays(path):
#     with open(path, "rb") as f:
#         d = f.read()
#         heif_file = pillow_heif.read_heif(bytearray(d))
#         assert heif_file is not None
#         width, height = heif_file.size
#         assert width > 0
#         assert height > 0
#         assert heif_file.brand != pillow_heif.constants.heif_brand_unknown_brand
#         assert len(heif_file.data) > 0
#
#
# @pytest.mark.parametrize("path", heif_files_wih_profiles)
# def test_read_icc_color_profile(path):
#     heif_file = pillow_heif.read_heif(path)
#     i = path.name.find("__")
#     expected_color_profile = path.name[i + 2 : i + 6]
#     if expected_color_profile == "none":
#         assert heif_file.color_profile is None
#         return
#     else:
#         assert heif_file.color_profile["type"] == expected_color_profile
#     if heif_file.color_profile["type"] in [
#         "prof",
#         "rICC",
#     ]:
#         profile = BytesIO(heif_file.color_profile["data"])
#         ImageCms.getOpenProfile(profile)


# @pytest.mark.parametrize("path", heic_files[:2] + hif_files[:2] + avif_files[:2])
# def test_read_pillow_frombytes(path):
#     heif_file = pillow_heif.read_heif(path)
#     to_pillow_image(heif_file)


@pytest.mark.parametrize("img_info", hif_images)
def test_10bit(img_info):
    heif_file = open_heif(Path(img_info["file"]), convert_hdr_to_8bit=False)
    assert not heif_file.convert_hdr_to_8bit
    heif_file.load()


@pytest.mark.parametrize("img_info", heic_images[:2] + hif_images[:2] + avif_images[:2])
def test_heif_open_load_close(img_info):
    heif_file = open_heif(Path(img_info["file"]))
    assert isinstance(heif_file, UndecodedHeifFile)
    assert heif_file.data is None
    heif_file.load()
    assert isinstance(heif_file, HeifFile)
    assert heif_file.data is not None
    heif_file.close()  # free decoded data.
    assert heif_file.data is None


@pytest.mark.parametrize("img_info", invalid_images)
def test_invalid_file(img_info):
    with pytest.raises(HeifError):
        read_heif(Path(img_info["file"]))
    with pytest.raises(HeifError):
        with builtins.open(Path(img_info["file"]), "rb") as f:
            read_heif(BytesIO(f.read()))
    with pytest.raises(HeifError):
        with builtins.open(Path(img_info["file"]), "rb") as f:
            read_heif(f)


def test_lib_version():
    assert libheif_version() == "1.12.0"
