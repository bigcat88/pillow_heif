from io import BytesIO

import pytest
from packaging.version import parse as parse_version
from PIL import Image
from PIL import __version__ as pil_version

import pillow_heif

pillow_heif.register_heif_opener()


@pytest.mark.skipif(not pillow_heif.options().hevc_enc, reason="Requires HEIF encoder.")
@pytest.mark.skipif(parse_version(pil_version) < parse_version("9.2.0"), reason="Requires Pillow >= 9.2")
@pytest.mark.parametrize(
    "im_format",
    (
        "PNG",
        "JPEG",
        "TIFF",
        "WEBP",
    ),
)
def test_exif_from_pillow(im_format):
    def pil_image_with_exif():
        _exif = Image.Exif()
        _exif[0x010E] = exif_desc_value
        _ = BytesIO()
        Image.new("RGB", (10, 10), 0).save(_, format=im_format, exif=_exif)
        return _

    exif_desc_value = "this is a desc"
    im = Image.open(pil_image_with_exif())
    exif = im.getexif()  # noqa
    assert exif[0x010E] == exif_desc_value
    out_im_heif = BytesIO()
    im.save(out_im_heif, format="HEIF")
    im_heif = Image.open(out_im_heif)
    assert im_heif.info["exif"]
    assert isinstance(im_heif.info["exif"], bytes)
    exif = im_heif.getexif()  # noqa
    assert exif[0x010E] == exif_desc_value
