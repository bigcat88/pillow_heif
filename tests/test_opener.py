import os
from io import BytesIO
from pathlib import Path
from unittest import mock
import pytest
from PIL import Image, ImageCms
from pillow_heif import register_heif_opener, check_heif_magic, HeifError


register_heif_opener()

os.chdir(os.path.dirname(os.path.abspath(__file__)))
heic_files = list(Path().glob("images/**/*.heic"))
hif_files = list(Path().glob("images/**/*.hif"))
avif_files = list(Path().glob("images/**/*.avif"))
heif_files = heic_files + hif_files + avif_files
heif_exif_test = [heif_file for heif_file in heif_files if heif_file.name.find("__") != -1]


@pytest.mark.parametrize("path", heic_files[:6] + hif_files[:6] + avif_files[:6])
def test_open_image(path):
    image = Image.open(path)
    image.load()
    assert image is not None


@pytest.mark.parametrize("path", heif_exif_test)
def test_open_image_exif(path):
    image = Image.open(path)
    if path.name.find("__none") == -1:
        assert image.info["exif"] is not None
    else:
        assert "exif" not in image.info


@pytest.mark.parametrize("path", heif_exif_test)
def test_icc_profile(path):
    image = Image.open(path)
    if path.name.find("__none") == -1 and path.name.find("__nclx") == -1:
        assert image.info.get("icc_profile") is not None
        icc_profile = BytesIO(image.info["icc_profile"])
        icc_profile = ImageCms.getOpenProfile(icc_profile)
    else:
        assert "icc_profile" not in image.info


@pytest.mark.parametrize(
    "magic",
    [b"heic", b"heix", b"heim", b"heis", b"hevc", b"hevx", b"hevm", b"hevs", b"mif1", b"msf1", b"avif", b"avis"],
)
def test_check_heif_magic(magic):
    assert check_heif_magic(b"    ftyp%b    " % magic)


def test_check_heif_magic_wrong():
    assert not check_heif_magic(b"    fty hei     ")


@mock.patch("pillow_heif.open_heif", side_effect=HeifError(code=1, subcode=2, message="Error"))
def test_open_image_error(open_mock):
    with pytest.raises(IOError):
        Image.open("invalid_path.heic")


@mock.patch.object(Image, "register_open")
@mock.patch.object(Image, "register_mime")
def test_register_heif_opener(
    register_open_mock,
    register_mime_mock,
):
    register_heif_opener()
    register_open_mock.assert_called_once()
    register_mime_mock.assert_called_once()
