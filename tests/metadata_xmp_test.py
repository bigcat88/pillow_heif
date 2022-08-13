import os
from io import BytesIO
from pathlib import Path

import helpers
import pytest
from packaging.version import parse as parse_version
from PIL import Image
from PIL import __version__ as pil_version
from PIL import features

import pillow_heif

os.chdir(os.path.dirname(os.path.abspath(__file__)))
pillow_heif.register_avif_opener()
pillow_heif.register_heif_opener()


@pytest.mark.skipif(not features.check("webp"), reason="Requires WEBP support.")
@pytest.mark.skipif(not helpers.aom_enc(), reason="Requires AVIF encoder.")
@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEIF encoder.")
@pytest.mark.skipif(parse_version(pil_version) < parse_version("8.3.0"), reason="Requires Pillow >= 8.3")
@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
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
    xmp = im.getxmp() if hasattr(im, "getxmp") else pillow_heif.getxmp(im.info["xmp"])  # noqa
    pytest.importorskip("defusedxml", reason="requires `defusedxml`")
    assert xmp["xmpmeta"]["RDF"]["Description"]["subject"]["Bag"]["li"] == "TestSubject"
    out_im_heif = BytesIO()
    im.save(out_im_heif, format=save_format)
    im_heif = Image.open(out_im_heif)
    assert im_heif.info["xmp"]
    assert isinstance(im_heif.info["xmp"], bytes)
    xmp_heif = im_heif.getxmp()  # noqa
    assert xmp_heif["xmpmeta"]["RDF"]["Description"]["subject"]["Bag"]["li"] == "TestSubject"


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEIF encoder.")
def test_pillow_xmp_add_remove():
    xmp_data = b"<xmp_data>"
    out_heif_no_xmp = BytesIO()
    out_heif = BytesIO()
    im = Image.new("RGB", (15, 15), 0)
    # filling `xmp` during save.
    im.save(out_heif, format="HEIF", xmp=xmp_data)
    assert "xmp" not in im.info or im.info["xmp"] is None
    im_heif = Image.open(out_heif)
    assert im_heif.info["xmp"]
    # filling `info["xmp"]` before save.
    im.info["xmp"] = xmp_data
    im.save(out_heif, format="HEIF")
    im_heif = Image.open(out_heif)
    assert im_heif.info["xmp"]
    # setting `xmp` to `None` during save.
    im_heif.save(out_heif_no_xmp, format="HEIF", xmp=None)
    assert im_heif.info["xmp"]
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


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEIF encoder.")
def test_heif_xmp_add_remove():
    xmp_data = b"<xmp_data>"
    out_heif_no_xmp = BytesIO()
    out_heif = BytesIO()
    # test filling `xmp` during save.
    im_heif = pillow_heif.from_pillow(Image.new("RGB", (15, 15), 0))
    im_heif.save(out_heif, xmp=xmp_data)
    assert "xmp" not in im_heif.info or im_heif.info["xmp"] is None
    im_heif = pillow_heif.open_heif(out_heif)
    assert im_heif.info["xmp"]
    # test filling `info["xmp"]` before save.
    im_heif = pillow_heif.from_pillow(Image.new("RGB", (15, 15), 0))
    im_heif.info["xmp"] = xmp_data
    im_heif.save(out_heif)
    im_heif = pillow_heif.open_heif(out_heif)
    assert im_heif.info["xmp"]
    # setting `xmp` to `None` during save.
    im_heif.save(out_heif_no_xmp, xmp=None)
    assert im_heif.info["xmp"]
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
