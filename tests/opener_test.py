import os
from io import BytesIO
from pathlib import Path
from unittest import mock
import pytest
from PIL import Image, ImageCms, UnidentifiedImageError
from pillow_heif import register_heif_opener, check_heif_magic, HeifError


register_heif_opener()

os.chdir(os.path.dirname(os.path.abspath(__file__)))
heic_files = [f for f in list(Path().glob("images/**/*.heic")) if f.name.find("__fail") == -1]
hif_files = [f for f in list(Path().glob("images/**/*.hif")) if f.name.find("__fail") == -1]
avif_files = [f for f in list(Path().glob("images/**/*.avif")) if f.name.find("__fail") == -1]
heif_files = heic_files + hif_files + avif_files
heif_exif_test = [f for f in heif_files if f.name.find("__") != -1]


@pytest.mark.parametrize("path", heic_files[:6] + hif_files[:6] + avif_files[:6])
def test_open_image(path):
    image = Image.open(path)
    assert image is not None


@pytest.mark.parametrize("path", heic_files[:2] + hif_files[:2] + avif_files[:2])
def test_verify(path):
    image = Image.open(path)
    image.verify()
    assert image is not None
    assert not getattr(image, "fp", None)
    image.load()


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
        ImageCms.getOpenProfile(icc_profile)
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
def test_open_image_error(open_heif_mock):
    with pytest.raises(IOError):
        Image.open("invalid_path.heic")


@mock.patch.object(Image, "register_open")
@mock.patch.object(Image, "register_mime")
@mock.patch.object(Image, "register_extensions")
def test_register_heif_opener(
    register_open_mock,
    register_mime_mock,
    register_extensions,
):
    register_heif_opener()
    register_open_mock.assert_called_once()
    assert register_mime_mock.call_count == 2
    register_extensions.assert_called_once()


def test_invalid_data():
    with pytest.raises(UnidentifiedImageError):
        Image.open("images/Pug/invalid__fail.heic")
