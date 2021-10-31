import os
from unittest import mock
import pytest
from PIL import Image
from pillow_heif import register_heif_opener, check_heif_magic


register_heif_opener()
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize(
    ['folder', 'image_name'],
    [
        ('Pug', 'PUG1.HEIC',),
        ('Pug', 'PUG2.HEIC',),
        ('Pug', 'PUG3.HEIC',),
        ('hif', '93FG5559.HIF',),
        ('hif', '93FG5564.HIF',),
    ]
)
def test_open_image(folder, image_name):
    image = Image.open(os.path.join(TESTS_DIR, 'images', folder, image_name))
    image.load()
    assert image is not None


@pytest.mark.parametrize(
    ['folder', 'image_name', 'present'],
    [
        ('Pug', 'PUG1.HEIC', True,),
        ('Pug', 'PUG2.HEIC', True,),
        ('Pug', 'PUG3.HEIC', False,),
        ('hif', '93FG5559.HIF', True,),
        ('hif', '93FG5564.HIF', True,),
    ]
)
def test_open_image_exif(folder, image_name, present):
    image = Image.open(os.path.join(TESTS_DIR, 'images', folder, image_name))
    if present:
        assert image.info['exif'] is not None
    else:
        assert 'exif' not in image.info


@pytest.mark.parametrize(
    ['magic'],
    [
        (b'heic',),
        (b'heix',),
        (b'hevc',),
        (b'hevx',),
        (b'heim',),
        (b'heis',),
        (b'hevm',),
        (b'hevs',),
        (b'mif1',),
    ]
)
def test_check_heif_magic(magic):
    assert check_heif_magic(b'    ftyp%b    ' % magic)


def test_check_heif_magic_wrong():
    assert not check_heif_magic(b'    fty hei     ')


@mock.patch.object(Image, 'register_open')
@mock.patch.object(Image, 'register_decoder')
@mock.patch.object(Image, 'register_extensions')
@mock.patch.object(Image, 'register_mime')
def test_register_heif_opener(
    register_open_mock,
    register_decoder_mock,
    register_extensions_mock,
    register_mime_mock,
):
    register_heif_opener()
    register_open_mock.assert_called_once()
    register_decoder_mock.assert_called_once()
    register_extensions_mock.assert_called_once()
    register_mime_mock.assert_called_once()
