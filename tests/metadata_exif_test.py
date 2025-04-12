from io import BytesIO

import helpers
import pytest
from PIL import Image, features

import pillow_heif

pillow_heif.register_heif_opener()


@pytest.mark.skipif(not features.check("webp"), reason="Requires WEBP support.")
@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("save_format", ("HEIF",))
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
        im_exif = Image.Exif()
        im_exif[0x010E] = exif_desc_value
        _ = BytesIO()
        Image.new("RGB", (16, 16), 0).save(_, format=im_format, exif=im_exif)
        return _

    exif_desc_value = "this is a desc"
    im = Image.open(pil_image_with_exif())
    exif = im.getexif()  # noqa
    assert exif[0x010E] == exif_desc_value
    out_im_heif = BytesIO()
    im.save(out_im_heif, format=save_format)  # saving to HEIF
    im_heif = Image.open(out_im_heif)
    assert im_heif.info["exif"]
    assert isinstance(im_heif.info["exif"], bytes)
    exif = im_heif.getexif()  # noqa
    assert exif[0x010E] == exif_desc_value
    out_im = BytesIO()
    im_heif.save(out_im, format=im_format, exif=im_heif.getexif())  # saving back to original format
    im = Image.open(out_im)
    exif = im.getexif()  # noqa
    assert exif[0x010E] == exif_desc_value


@pytest.mark.skipif(not features.check("webp"), reason="Requires WEBP support.")
@pytest.mark.parametrize(
    "img",
    (
        "images/heif_other/arrow.heic",
        "images/heif_other/cat.hif",
        "images/heif_other/pug.heic",
        "images/heif_special/xiaomi.heic",
    ),
)
@pytest.mark.parametrize("im_format", ("JPEG", "PNG", "WEBP"))
def test_exif_from_heif_to_pillow(img, im_format):
    heif_file = pillow_heif.open_heif(img)
    out_pillow = BytesIO()
    heif_exif_bytes = heif_file.info["exif"]
    if img == "images/heif_special/xiaomi.heic" and im_format == "JPEG":  # JPEG do not support EXIF bigger 65k
        return
    Image.linear_gradient("L").save(out_pillow, format=im_format, exif=heif_exif_bytes)
    im = Image.open(out_pillow)
    pillow_exif = im.getexif()
    im.close()
    heif_exif = Image.Exif()
    heif_exif.load(heif_exif_bytes)
    assert pillow_exif == heif_exif


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
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


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
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


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
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


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
def test_corrupted_exif():
    exif_data = b"This_is_not_valid_EXIF_data"
    out_im = BytesIO()
    helpers.gradient_rgb().save(out_im, format="HEIF", exif=exif_data)
    im = Image.open(out_im)
    with pytest.raises(SyntaxError):
        im.getexif()
    assert im.info["exif"] == exif_data


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
def test_exif_as_class():
    exif = Image.Exif()
    exif[258] = 8
    exif[40963] = 455
    exif[305] = "exif test"
    out_im = BytesIO()
    helpers.gradient_rgb().save(out_im, format="HEIF", exif=exif)
    im = Image.open(out_im)
    exif = im.getexif()
    assert exif[258] == 8
    assert exif[40963] == 455
    assert exif[305] == "exif test"


def test_xiaomi_exif():
    im = Image.open("images/heif_special/xiaomi.heic")
    im.getexif()
    im.load()


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
def test_data_before_exif():
    exif = Image.Exif()
    exif_bytes = exif.tobytes()
    exif_full_data = b"hidden data " + exif_bytes
    out_im = BytesIO()
    helpers.gradient_rgb().save(out_im, format="HEIF", exif=exif_full_data)
    im = Image.open(out_im)
    out_im.seek(0)
    assert out_im.read().find(b"hidden data ") != -1  # checking that this was saved
    assert im.getexif() == exif
    assert im.info["exif"] == exif_bytes


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
def test_empty_exif():
    exif = Image.Exif()
    out_im = BytesIO()
    helpers.gradient_rgb().save(out_im, format="HEIF", exif=exif.tobytes())
    im = Image.open(out_im)
    assert im.getexif() == exif
    assert im.info["exif"] == exif.tobytes()
