import os
from io import BytesIO
from pathlib import Path

import helpers
import pytest
from PIL import Image, features

import pillow_heif

pytest.importorskip("defusedxml", reason="defusedxml not installed")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
pillow_heif.register_heif_opener()


@pytest.mark.skipif(not features.check("webp"), reason="Requires WEBP support.")
@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("save_format", ("HEIF",))
@pytest.mark.parametrize(
    "img_path",
    (
        "images/non_heif/xmp.png",
        "images/non_heif/xmp.jpeg",
        "images/non_heif/xmp.tiff",
        "images/non_heif/xmp.webp",
    ),
)
def test_xmp_from_pillow(img_path, save_format):
    im = Image.open(Path(img_path))
    xmp = im.getxmp()  # noqa
    assert xmp["xmpmeta"]["RDF"]["Description"]["subject"]["Bag"]["li"] == "TestSubject"
    out_im_heif = BytesIO()
    im.save(out_im_heif, format=save_format)
    im_heif = Image.open(out_im_heif)
    assert im_heif.info["xmp"]
    assert isinstance(im_heif.info["xmp"], bytes)
    xmp_heif = im_heif.getxmp()  # noqa
    assert xmp_heif["xmpmeta"]["RDF"]["Description"]["subject"]["Bag"]["li"] == "TestSubject"


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
def test_pillow_xmp_add_remove():
    xmp_data = b"<xmp_data>"
    out_heif_no_xmp = BytesIO()
    out_heif = BytesIO()
    im = Image.new("RGB", (15, 15), 0)
    # filling `xmp` during save.
    im.save(out_heif, format="HEIF", xmp=xmp_data)
    assert "xmp" not in im.info or im.info["xmp"] is None
    im_heif = Image.open(out_heif)
    assert im_heif.info["xmp"] == xmp_data
    # filling `info["xmp"]` before save.
    im.info["xmp"] = xmp_data
    im.save(out_heif, format="HEIF")
    im_heif = Image.open(out_heif)
    assert im_heif.info["xmp"] == xmp_data
    # setting `xmp` to `None` during save.
    im_heif.save(out_heif_no_xmp, format="HEIF", xmp=None)
    assert im_heif.info["xmp"] == xmp_data
    im_heif_no_xmp = Image.open(out_heif_no_xmp)
    assert "xmp" not in im_heif_no_xmp.info or im_heif_no_xmp.info["xmp"] is None
    # filling `info["xmp"]` with `None` before save.
    im_heif.info["xmp"] = None
    im_heif.save(out_heif_no_xmp, format="HEIF")
    im_heif_no_xmp = Image.open(out_heif_no_xmp)
    assert "xmp" not in im_heif_no_xmp.info or im_heif_no_xmp.info["xmp"] is None
    # removing `info["xmp"]` before save.
    im_heif.info.pop("xmp")
    im_heif.save(out_heif_no_xmp, format="HEIF")
    im_heif_no_xmp = Image.open(out_heif_no_xmp)
    assert "xmp" not in im_heif_no_xmp.info or im_heif_no_xmp.info["xmp"] is None


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
def test_heif_xmp_add_remove():
    xmp_data = b"<xmp_data>"
    out_heif_no_xmp = BytesIO()
    out_heif = BytesIO()
    # test filling `xmp` during save.
    im_heif = pillow_heif.from_pillow(Image.new("RGB", (15, 15), 0))
    im_heif.save(out_heif, xmp=xmp_data)
    assert "xmp" not in im_heif.info or im_heif.info["xmp"] is None
    im_heif = pillow_heif.open_heif(out_heif)
    assert im_heif.info["xmp"] == xmp_data
    # test filling `info["xmp"]` before save.
    im_heif = pillow_heif.from_pillow(Image.new("RGB", (15, 15), 0))
    im_heif.info["xmp"] = xmp_data
    im_heif.save(out_heif)
    im_heif = pillow_heif.open_heif(out_heif)
    assert im_heif.info["xmp"] == xmp_data
    # setting `xmp` to `None` during save.
    im_heif.save(out_heif_no_xmp, xmp=None)
    assert im_heif.info["xmp"] == xmp_data
    im_heif_no_xmp = pillow_heif.open_heif(out_heif_no_xmp)
    assert "xmp" not in im_heif_no_xmp.info or im_heif_no_xmp.info["xmp"] is None
    # filling `info["xmp"]` with `None` before save.
    im_heif.info["xmp"] = None
    im_heif.save(out_heif_no_xmp)
    im_heif_no_xmp = pillow_heif.open_heif(out_heif_no_xmp)
    assert "xmp" not in im_heif_no_xmp.info or im_heif_no_xmp.info["xmp"] is None
    # removing `info["xmp"]` before save.
    im_heif.info.pop("xmp")
    im_heif.save(out_heif_no_xmp)
    im_heif_no_xmp = pillow_heif.open_heif(out_heif_no_xmp)
    assert "xmp" not in im_heif_no_xmp.info or im_heif_no_xmp.info["xmp"] is None


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
def test_heif_xmp_latin1_with_zero_byte():
    im = Image.open("images/heif_other/L_xmp_latin1.heic")
    out_heif = BytesIO()
    im.save(out_heif, format="HEIF")
    out_im = Image.open(out_heif)
    assert im.getxmp() == out_im.getxmp()  # noqa
    assert out_im.info["xmp"][-1] == 0  # check null byte not to get lost
