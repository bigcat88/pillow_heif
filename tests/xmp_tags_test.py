import os
from io import BytesIO
from pathlib import Path

import pytest
from packaging.version import parse as parse_version
from PIL import Image
from PIL import __version__ as pil_version

import pillow_heif

os.chdir(os.path.dirname(os.path.abspath(__file__)))
pillow_heif.register_heif_opener()


@pytest.mark.skipif(not pillow_heif.options().hevc_enc, reason="Requires HEIF encoder.")
@pytest.mark.skipif(parse_version(pil_version) < parse_version("8.3.0"), reason="Requires Pillow >= 8.3")
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


@pytest.mark.skipif(not pillow_heif.options().hevc_enc, reason="Requires HEIF encoder.")
def test_pillow_xmp_add_remove():
    xmp_data = b"<xmp_data>"
    im = Image.new("RGB", (15, 15), 0)
    out_heif = BytesIO()
    # test `xmp=` during save.
    im.save(out_heif, format="HEIF", xmp=xmp_data)
    assert "xmp" not in im.info
    im_heif = Image.open(out_heif)
    assert im_heif.info["xmp"]
    # test `info["xmp"]= ` before save.
    im.info["xmp"] = xmp_data
    im.save(out_heif, format="HEIF")
    im_heif = Image.open(out_heif)
    assert im_heif.info["xmp"]

    # heif_file = open_heif(Path("images/rgb8_128_128_2_1.heic"))
    # # No XMP in images
    # for frame in heif_file:
    #     assert not frame.info["xmp"]
    # out_buf =
    # heif_file.save(out_buf, xmp=xmp_data, save_all=True)
    # # Checking `heif_file` to not change
    # for frame in heif_file:
    #     assert not frame.info["xmp"]
    # saved_heif = open_heif(out_buf)
    # # Checking that output  of`heif_file` was changed
    # for i, frame in enumerate(saved_heif):
    #     assert not frame.info["xmp"] if i else frame.info["xmp"]
    # out_buf2 = BytesIO()
    # # Remove XMP from primary image
    # saved_heif.save(out_buf2, xmp=None, save_all=True)
    # # Checking `saved_heif` to not change
    # for i, frame in enumerate(saved_heif):
    #     assert not frame.info["xmp"] if i else frame.info["xmp"]
    # saved_heif2 = open_heif(out_buf2)
    # # Checking that output has no XMP
    # for i, frame in enumerate(saved_heif2):
    #     assert not frame.info["xmp"]
