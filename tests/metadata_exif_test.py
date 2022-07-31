from io import BytesIO

import helpers
import pytest
from packaging.version import parse as parse_version
from PIL import Image
from PIL import __version__ as pil_version
from PIL import features

import pillow_heif

pillow_heif.register_avif_opener()
pillow_heif.register_heif_opener()


@pytest.mark.skipif(not features.check("webp"), reason="Requires WEBP support.")
@pytest.mark.skipif(not helpers.aom_enc(), reason="Requires AVIF encoder.")
@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEIF encoder.")
@pytest.mark.skipif(parse_version(pil_version) < parse_version("9.2.0"), reason="Requires Pillow >= 9.2")
@pytest.mark.parametrize("save_format", ("HEIF", "AVIF"))
@pytest.mark.parametrize(
    "im_format",
    (
        "PNG",
        "JPEG",
        "TIFF",
        "WEBP",
    ),
)
def test_exif_from_pillow(im_format, save_format):
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
    im.save(out_im_heif, format=save_format)
    im_heif = Image.open(out_im_heif)
    assert im_heif.info["exif"]
    assert isinstance(im_heif.info["exif"], bytes)
    exif = im_heif.getexif()  # noqa
    assert exif[0x010E] == exif_desc_value


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEIF encoder.")
def test_pillow_exif_add_remove():
    exif_desc_value = "this is a desc"
    exif = Image.Exif()
    exif[0x010E] = exif_desc_value
    out_heif_no_exif = BytesIO()
    out_heif = BytesIO()
    im = Image.new("RGB", (15, 15), 0)
    # filling `exif` during save.
    im.save(out_heif, format="HEIF", exif=exif.tobytes())
    assert "exif" not in im.info or im.info["exif"] is None
    im_heif = Image.open(out_heif)
    assert im_heif.info["exif"]
    # filling `info["exif"]` before save.
    im.info["exif"] = exif.tobytes()
    im.save(out_heif, format="HEIF")
    im_heif = Image.open(out_heif)
    assert im_heif.info["exif"]
    # setting `exif` to `None` during save.
    im_heif.save(out_heif_no_exif, format="HEIF", exif=None)
    assert im_heif.info["exif"]
    im_heif_no_exif = Image.open(out_heif_no_exif)
    assert "exif" not in im_heif_no_exif.info or im_heif_no_exif.info["exif"] is None
    # filling `info["exif"]` with `None` before save.
    im_heif.info["exif"] = None
    im_heif.save(out_heif_no_exif, format="HEIF")
    im_heif_no_exif = Image.open(out_heif_no_exif)
    assert "exif" not in im_heif_no_exif.info or im_heif_no_exif.info["exif"] is None
    # removing `info["exif"]` before save.
    im_heif.info.pop("exif")
    im_heif.save(out_heif_no_exif, format="HEIF")
    im_heif_no_exif = Image.open(out_heif_no_exif)
    assert "exif" not in im_heif_no_exif.info or im_heif_no_exif.info["exif"] is None


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEIF encoder.")
def test_heif_exif_add_remove():
    exif_desc_value = "this is a desc"
    exif = Image.Exif()
    exif[0x010E] = exif_desc_value
    out_heif_no_exif = BytesIO()
    out_heif = BytesIO()
    # test filling `exif` during save.
    im_heif = pillow_heif.from_pillow(Image.new("RGB", (15, 15), 0))
    im_heif.save(out_heif, exif=exif.tobytes())
    assert "exif" not in im_heif.info or im_heif.info["exif"] is None
    im_heif = pillow_heif.open_heif(out_heif)
    assert im_heif.info["exif"]
    # test filling `info["exif"]` before save.
    im_heif = pillow_heif.from_pillow(Image.new("RGB", (15, 15), 0))
    im_heif.info["exif"] = exif.tobytes()
    im_heif.save(out_heif)
    im_heif = pillow_heif.open_heif(out_heif)
    assert im_heif.info["exif"]
    # setting `exif` to `None` during save.
    im_heif.save(out_heif_no_exif, exif=None)
    assert im_heif.info["exif"]
    im_heif_no_exif = pillow_heif.open_heif(out_heif_no_exif)
    assert "exif" not in im_heif_no_exif.info or im_heif_no_exif.info["exif"] is None
    # filling `info["exif"]` with `None` before save.
    im_heif.info["exif"] = None
    im_heif.save(out_heif_no_exif)
    im_heif_no_exif = pillow_heif.open_heif(out_heif_no_exif)
    assert "exif" not in im_heif_no_exif.info or im_heif_no_exif.info["exif"] is None
    # removing `info["exif"]` before save.
    im_heif.info.pop("exif")
    im_heif.save(out_heif_no_exif)
    im_heif_no_exif = pillow_heif.open_heif(out_heif_no_exif)
    assert "exif" not in im_heif_no_exif.info or im_heif_no_exif.info["exif"] is None


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEIF encoder.")
def test_heif_multi_frame_exif_add_remove():
    exif_desc_value = "this is a desc"
    exif = Image.Exif()
    exif[0x010E] = exif_desc_value
    out_heif_no_exif = BytesIO()
    out_heif = BytesIO()
    # test filling `exif` during save.
    im_heif = pillow_heif.from_pillow(Image.new("RGB", (15, 15), 0))
    im_heif.add_from_pillow(Image.new("RGB", (13, 13), 0))
    im_heif.save(out_heif, exif=exif.tobytes(), primary_index=1)
    for i in range(2):
        assert "exif" not in im_heif[i].info or im_heif[i].info["exif"] is None
    im_heif = pillow_heif.open_heif(out_heif)
    assert im_heif[1].info["exif"] and not im_heif[0].info["exif"]
    # test filling `info["exif"]` before save.
    im_heif = pillow_heif.from_pillow(Image.new("RGB", (15, 15), 0))
    im_heif.add_from_pillow(Image.new("RGB", (13, 13), 0))
    im_heif[1].info["exif"] = exif.tobytes()
    im_heif.save(out_heif, primary_index=1)
    im_heif = pillow_heif.open_heif(out_heif)
    assert im_heif[1].info["exif"] and not im_heif[0].info["exif"]
    # setting `exif` to `None` during save.
    im_heif.save(out_heif_no_exif, exif=None)
    assert im_heif[1].info["exif"] and not im_heif[0].info["exif"]
    im_heif_no_exif = pillow_heif.open_heif(out_heif_no_exif)
    assert "exif" not in im_heif_no_exif[0].info or im_heif_no_exif[0].info["exif"] is None
    assert "exif" not in im_heif_no_exif[1].info or im_heif_no_exif[1].info["exif"] is None
    # filling `info["exif"]` with `None` before save.
    im_heif.info["exif"] = None
    im_heif.save(out_heif_no_exif)
    im_heif_no_exif = pillow_heif.open_heif(out_heif_no_exif)
    assert "exif" not in im_heif_no_exif[0].info or im_heif_no_exif[0].info["exif"] is None
    assert "exif" not in im_heif_no_exif[1].info or im_heif_no_exif[1].info["exif"] is None
    # removing `info["exif"]` before save.
    im_heif.info.pop("exif")
    im_heif.save(out_heif_no_exif)
    im_heif_no_exif = pillow_heif.open_heif(out_heif_no_exif)
    assert "exif" not in im_heif_no_exif[0].info or im_heif_no_exif[0].info["exif"] is None
    assert "exif" not in im_heif_no_exif[1].info or im_heif_no_exif[1].info["exif"] is None
