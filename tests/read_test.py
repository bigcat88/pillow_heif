import os
from gc import collect
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image, ImageCms
import pillow_heif


os.chdir(os.path.dirname(os.path.abspath(__file__)))
heic_files = [f for f in list(Path().glob("images/**/*.heic")) if f.name.find("__fail") == -1]
hif_files = [f for f in list(Path().glob("images/**/*.hif")) if f.name.find("__fail") == -1]
avif_files = [f for f in list(Path().glob("images/**/*.avif")) if f.name.find("__fail") == -1]
heif_files = heic_files + hif_files + avif_files
heif_files_wih_profiles = [f for f in heif_files if f.name.find("__") != -1]


@pytest.mark.parametrize("path", heif_files)
def test_check(path):
    filetype = pillow_heif.check_heif(path)
    assert pillow_heif.heif_filetype_no != filetype
    unsupported_list = [
        "rally_burst.heic",
        "bird_burst.heic",
        "starfield_animation.heic",
        "sea1_animation.heic",
    ]
    if os.path.basename(path) in unsupported_list:
        assert pillow_heif.heif_filetype_yes_unsupported == filetype
    else:
        assert pillow_heif.heif_filetype_yes_unsupported != filetype


@pytest.mark.parametrize("path", heif_files[:2])
def test_get_bytes_from_path(path):
    d = pillow_heif.reader._get_bytes(path)
    assert d == path.read_bytes()


@pytest.mark.parametrize("path", heif_files[:2])
def test_get_bytes_from_file_name(path):
    d = pillow_heif.reader._get_bytes(str(path))
    assert d == path.read_bytes()


@pytest.mark.parametrize("path", heif_files[:2])
def test_get_bytes_from_file_object(path):
    with open(path, "rb") as f:
        d = pillow_heif.reader._get_bytes(f)
    assert d == path.read_bytes()


@pytest.mark.parametrize("path", heif_files[:2])
def test_get_bytes_from_bytes(path):
    with open(path, "rb") as f:
        d = pillow_heif.reader._get_bytes(f.read())
    assert d == path.read_bytes()


@pytest.fixture(scope="session", params=heif_files)
def heif_file(request):
    return pillow_heif.read_heif(request.param)


@pytest.mark.parametrize("path", heif_files)
def test_open_and_load(path):
    heif_file = pillow_heif.open_heif(path)
    assert heif_file.size[0] > 0
    assert heif_file.size[1] > 0
    assert heif_file.has_alpha is not None
    assert heif_file.mode is not None
    assert heif_file.bit_depth is not None

    assert heif_file.data is None
    assert heif_file.stride is None

    if path.name == "arrow__prof.heic":
        assert heif_file.metadata
        assert heif_file.color_profile

    res = heif_file.load()
    assert heif_file is res
    assert heif_file.data is not None
    assert heif_file.stride is not None
    assert len(heif_file.data) >= heif_file.stride * heif_file.size[1]
    assert type(heif_file.data[:100]) == bytes
    assert str(heif_file).find("HeifFile") != -1

    # Subsequent calls don't change anything
    res = heif_file.load()
    assert heif_file is res
    assert heif_file.data is not None
    assert heif_file.stride is not None
    heif_file.close()


@pytest.mark.parametrize("path", heif_files)
def test_open_and_load_data_not_collected(path):
    data = path.read_bytes()
    heif_file = pillow_heif.open_heif(data)
    data = None  # heif_file.load() should work even if there is no other refs to the source data.
    collect()
    heif_file.load()


def to_pillow_image(heif_file):
    return Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )


@pytest.mark.parametrize("path", heic_files)
def test_read_bytes(path):
    with open(path, "rb") as f:
        d = f.read()
        heif_file = pillow_heif.read_heif(d)
        assert heif_file is not None
        width, height = heif_file.size
        assert width > 0
        assert height > 0
        assert heif_file.brand != pillow_heif.constants.heif_brand_unknown_brand
        assert len(heif_file.data) > 0


@pytest.mark.parametrize("path", heic_files[:2])
def test_read_bytearrays(path):
    with open(path, "rb") as f:
        d = f.read()
        heif_file = pillow_heif.read_heif(bytearray(d))
        assert heif_file is not None
        width, height = heif_file.size
        assert width > 0
        assert height > 0
        assert heif_file.brand != pillow_heif.constants.heif_brand_unknown_brand
        assert len(heif_file.data) > 0


@pytest.mark.parametrize("path", heif_files_wih_profiles)
def test_read_icc_color_profile(path):
    heif_file = pillow_heif.read_heif(path)
    i = path.name.find("__")
    expected_color_profile = path.name[i + 2 : i + 6]
    if expected_color_profile == "none":
        assert heif_file.color_profile is None
        return
    else:
        assert heif_file.color_profile["type"] == expected_color_profile
    if heif_file.color_profile["type"] in [
        "prof",
        "rICC",
    ]:
        profile = BytesIO(heif_file.color_profile["data"])
        ImageCms.getOpenProfile(profile)


@pytest.mark.parametrize("path", heic_files[:2] + hif_files[:2] + avif_files[:2])
def test_read_pillow_frombytes(path):
    heif_file = pillow_heif.read_heif(path)
    to_pillow_image(heif_file)


@pytest.mark.parametrize("path", hif_files)
def test_10bit(path):
    heif_file = pillow_heif.read_heif(path, convert_hdr_to_8bit=False)
    heif_file.load()


@pytest.mark.parametrize("path", heic_files[:1] + hif_files[:1] + avif_files[:1])
def test_super_heif_close(path):
    heif_file = pillow_heif.open_heif(path)
    heif_file.load()
    pillow_heif.HeifFile.close(heif_file)  # free decoded data.
    heif_file.close()
    return heif_file.data is None


def test_invalid_data():
    data = b"    ftypheic    0000"
    try:
        pillow_heif.read_heif(data)
    except pillow_heif.HeifError as exception:
        assert str(exception).find("Invalid input: No 'ftyp' box") != -1
        assert str(repr(exception)).startswith("HeifError")


def test_invalid_file():
    with pytest.raises(ValueError):
        pillow_heif.read_heif(os.path.abspath(__file__))


def test_lib_version():
    assert pillow_heif.libheif_version() == "1.12.0"
