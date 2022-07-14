import os
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

import pillow_heif

os.chdir(os.path.dirname(os.path.abspath(__file__)))
pillow_heif.register_heif_opener()


@pytest.mark.skipif(not pillow_heif.options().hevc_enc, reason="Requires HEIF encoder.")
@pytest.mark.parametrize(
    "img_path",
    (
        "images/jpeg_gif_png/xmp.png",
        "images/jpeg_gif_png/xmp.jpeg",
        "images/jpeg_gif_png/xmp.tiff",
        "images/jpeg_gif_png/xmp.webp",
    ),
)
def test_xmp_from_png(img_path):
    im = Image.open(Path(img_path))
    xmp = im.getxmp() if hasattr(im, "getxmp") else pillow_heif.getxmp(im.info["xmp"])  # noqa
    assert xmp["xmpmeta"]["RDF"]["Description"]["subject"]["Bag"]["li"] == "TestSubject"
    out_im_heif = BytesIO()
    im.save(out_im_heif, format="HEIF")
    im_heif = Image.open(out_im_heif)
    assert im_heif.info["xmp"]
    assert isinstance(im_heif.info["xmp"], bytes)
    xmp_heif = im_heif.getxmp()  # noqa
    assert xmp_heif["xmpmeta"]["RDF"]["Description"]["subject"]["Bag"]["li"] == "TestSubject"
