from io import BytesIO

import pytest
from helpers import create_heif, hevc_enc
from PIL import Image

import pillow_heif

pillow_heif.register_heif_opener()


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("save_format", ("HEIF",))
def test_heif_primary_image(save_format):
    heif_buf = create_heif((64, 64), n_images=3, primary_index=1, format=save_format)
    heif_file = pillow_heif.open_heif(heif_buf)
    assert heif_file.primary_index == 1
    assert heif_file[1].info["primary"]
    out_buf = BytesIO()
    heif_file.save(out_buf, quality=1, format=save_format)
    heif_file_out = pillow_heif.open_heif(out_buf)
    assert heif_file_out.primary_index == 1
    assert heif_file_out[1].info["primary"]
    heif_file.save(out_buf, quality=1, primary_index=0, format=save_format)
    assert heif_file.primary_index == 1
    heif_file_out = pillow_heif.open_heif(out_buf)
    assert heif_file_out.primary_index == 0
    heif_file.save(out_buf, quality=1, primary_index=-1, format=save_format)
    assert heif_file.primary_index == 1
    heif_file_out = pillow_heif.open_heif(out_buf)
    assert heif_file_out.primary_index == 2
    heif_file.save(out_buf, quality=1, primary_index=99, format=save_format)
    assert heif_file.primary_index == 1
    heif_file_out = pillow_heif.open_heif(out_buf)
    assert heif_file_out.primary_index == 2


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("save_format", ("HEIF",))
def test_pillow_primary_image(save_format):
    heif_buf = create_heif((64, 64), n_images=3, primary_index=1, format=save_format)
    heif_file = Image.open(heif_buf)
    assert heif_file.tell() == 1
    assert heif_file.info["primary"]
    out_buf = BytesIO()
    heif_file.save(out_buf, format=save_format, save_all=True, quality=1)
    heif_file_out = Image.open(out_buf)
    assert heif_file_out.tell() == 1
    assert heif_file_out.info["primary"]
    heif_file.save(out_buf, format=save_format, save_all=True, quality=1, primary_index=0)
    assert heif_file.tell() == 1
    heif_file_out = Image.open(out_buf)
    assert heif_file_out.tell() == 0
    heif_file.save(out_buf, format=save_format, save_all=True, quality=1, primary_index=-1)
    assert heif_file.tell() == 1
    heif_file_out = Image.open(out_buf)
    assert heif_file_out.tell() == 2
    heif_file.save(out_buf, format=save_format, save_all=True, quality=1, primary_index=99)
    assert heif_file.tell() == 1
    heif_file_out = Image.open(out_buf)
    assert heif_file_out.tell() == 2


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("save_format", ("HEIF",))
def test_heif_info_changing(save_format):
    xmp = b"LeagueOf"
    exif_desc_value = "this is a desc"
    exif = Image.Exif()
    exif[0x010E] = exif_desc_value
    heif_buf = create_heif((64, 64), n_images=3, primary_index=1, exif=exif.tobytes(), xmp=xmp, format=save_format)
    im = pillow_heif.open_heif(heif_buf)
    assert im.info["primary"] and len(im.info["exif"]) > 0 and im.info["xmp"]
    out_buf = BytesIO()
    # Remove exif and xmp of a Primary Image.
    im.save(out_buf, exif=None, xmp=None, format=save_format)
    assert im.info["primary"] and len(im.info["exif"]) > 0 and im.info["xmp"]
    im_out = pillow_heif.open_heif(out_buf)
    for i in range(3):
        if i == 1:
            assert im_out[i].info["primary"] and not im_out[i].info["exif"] and "xmp" not in im_out[i].info
        else:
            assert not im_out[i].info["primary"] and not im_out[i].info["exif"] and "xmp" not in im_out[i].info
    # Set exif and xmp of all images. Change Primary Image to be last.
    for i in range(3):
        im[i].info["xmp"] = xmp
        im[i].info["exif"] = exif.tobytes()
        im[i].info["primary"] = bool(i == 2)
    im.save(out_buf, format=save_format)
    im_out = pillow_heif.open_heif(out_buf)
    assert im_out.info["primary"]
    assert im_out.primary_index == 2
    for i in range(3):
        assert im_out[i].info["exif"] and im_out[i].info["xmp"]
    # Remove `primary`, `xmp`, `exif` from info dict.
    for i in range(3):
        im[i].info.pop("xmp")
        im[i].info.pop("exif")
        im[i].info.pop("primary")
    im.save(out_buf, format=save_format)
    im_out = pillow_heif.open_heif(out_buf)
    assert im_out.info["primary"]
    assert im_out.primary_index == 0
    for i in range(3):
        assert not im_out[i].info["exif"] and "xmp" not in im_out[i].info


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("save_format", ("HEIF",))
def test_pillow_info_changing(save_format):
    xmp = b"LeagueOf"
    exif_desc_value = "this is a desc"
    exif = Image.Exif()
    exif[0x010E] = exif_desc_value
    heif_buf = create_heif((64, 64), n_images=3, primary_index=1, exif=exif.tobytes(), xmp=xmp, format=save_format)
    im = Image.open(heif_buf)
    assert im.info["primary"] and len(im.info["exif"]) > 0 and im.info["xmp"]
    out_buf = BytesIO()
    # Remove exif and xmp of a Primary Image.
    im.save(out_buf, format=save_format, save_all=True, exif=None, xmp=None)
    assert im.info["primary"] and len(im.info["exif"]) > 0 and im.info["xmp"]
    im_out = Image.open(out_buf)
    for i in range(3):
        im_out.seek(i)
        if i == 1:
            assert im_out.info["primary"] and not im_out.info["exif"] and "xmp" not in im_out.info
        else:
            assert not im_out.info["primary"] and not im_out.info["exif"] and "xmp" not in im_out.info
    # Set exif and xmp of all images. Change Primary Image to be last.
    for i in range(3):
        im.seek(i)
        im.info["xmp"] = xmp
        im.info["exif"] = exif.tobytes()
        im.info["primary"] = bool(i == 2)
    im.save(out_buf, format=save_format, save_all=True)
    im_out = Image.open(out_buf)
    assert im_out.info["primary"]
    assert im_out.tell() == 2
    for i in range(3):
        im_out.seek(i)
        assert im_out.info["exif"] and im_out.info["xmp"]
    # Remove `primary`, `xmp`, `exif` from info dict.
    for i in range(3):
        im.seek(i)
        im.info.pop("xmp")
        im.info.pop("exif")
        im.info.pop("primary")
    im.save(out_buf, format=save_format, save_all=True)
    im_out = Image.open(out_buf)
    assert im_out.info["primary"]
    assert im_out.tell() == 0
    for i in range(3):
        im_out.seek(i)
        assert not im_out.info["exif"] and "xmp" not in im_out.info


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("save_format", ("HEIF",))
def test_heif_iptc_metadata(save_format):
    heif_buf = create_heif((64, 64), format=save_format)
    data = (
        b"\x1c\x02Z\x00\x08Budapest"
        b"\x1c\x02e\x00\x07Hungary"
        b"\x1c\x02\x19\x00\x03HvK"
        b"\x1c\x02\x19\x00\x042006"
        b"\x1c\x02\x19\x00\x06summer"
        b"\x1c\x02\x19\x00\x04July"
        b"\x1c\x02\x19\x00\x07holiday"
        b"\x1c\x02\x19\x00\x07Hungary"
        b"\x1c\x02\x19\x00\x08Budapest"
    )
    iptc_metadata = {"type": "iptc", "data": data, "content_type": ""}
    im = pillow_heif.open_heif(heif_buf)
    im.info["metadata"].append(iptc_metadata)
    out_buf = BytesIO()
    im.save(out_buf, format=save_format)
    im_out = pillow_heif.open_heif(out_buf)
    assert im_out.info["metadata"]
    assert im_out.info["metadata"][0]["type"] == "iptc"
    assert im_out.info["metadata"][0]["data"] == data
    assert im_out.info["metadata"][0]["content_type"] == ""


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("save_format", ("HEIF",))
def test_pillow_iptc_metadata(save_format):
    heif_buf = create_heif((64, 64), format=save_format)
    data = (
        b"\x1c\x02Z\x00\x08Budapest"
        b"\x1c\x02e\x00\x07Hungary"
        b"\x1c\x02\x19\x00\x03HvK"
        b"\x1c\x02\x19\x00\x042006"
        b"\x1c\x02\x19\x00\x06summer"
        b"\x1c\x02\x19\x00\x04July"
        b"\x1c\x02\x19\x00\x07holiday"
        b"\x1c\x02\x19\x00\x07Hungary"
        b"\x1c\x02\x19\x00\x08Budapest"
    )
    iptc_metadata = {"type": "iptc", "data": data, "content_type": ""}
    im = Image.open(heif_buf)
    im.info["metadata"].append(iptc_metadata)
    out_buf = BytesIO()
    im.save(out_buf, format=save_format)
    im_out = Image.open(out_buf)
    assert im_out.info["metadata"]
    assert im_out.info["metadata"][0]["type"] == "iptc"
    assert im_out.info["metadata"][0]["data"] == data
    assert im_out.info["metadata"][0]["content_type"] == ""


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("save_format", ("HEIF",))
def test_heif_pixel_aspect_ratio_absent(save_format):
    heif_buf = create_heif((64, 64), format=save_format)
    heif_file = pillow_heif.open_heif(heif_buf)
    assert "pixel_aspect_ratio" not in heif_file[0].info


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("save_format", ("HEIF",))
@pytest.mark.parametrize("aspect_h,aspect_v", [(2, 1), (1, 2), (16, 9), (4, 3)])
def test_heif_pixel_aspect_ratio_roundtrip(save_format, aspect_h, aspect_v):
    heif_file = pillow_heif.HeifFile()
    heif_file.add_from_pillow(Image.effect_mandelbrot((64, 64), (-3, -2.5, 2, 2.5), 100))
    heif_file[0].info["pixel_aspect_ratio"] = (aspect_h, aspect_v)
    buf1 = BytesIO()
    heif_file.save(buf1, format=save_format)
    heif_out1 = pillow_heif.open_heif(buf1)
    assert heif_out1[0].info["pixel_aspect_ratio"] == (aspect_h, aspect_v)
    buf2 = BytesIO()
    heif_out1.save(buf2, format=save_format)
    heif_out2 = pillow_heif.open_heif(buf2)
    assert heif_out2[0].info["pixel_aspect_ratio"] == (aspect_h, aspect_v)


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("save_format", ("HEIF",))
def test_pillow_pixel_aspect_ratio_roundtrip(save_format):
    im = Image.effect_mandelbrot((64, 64), (-3, -2.5, 2, 2.5), 100)
    buf1 = BytesIO()
    im.save(buf1, format=save_format, pixel_aspect_ratio=(4, 3))
    im1 = Image.open(buf1)
    im1.load()
    assert im1.info["pixel_aspect_ratio"] == (4, 3)
    buf2 = BytesIO()
    im1.save(buf2, format=save_format)
    im2 = Image.open(buf2)
    im2.load()
    assert im2.info["pixel_aspect_ratio"] == (4, 3)


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize("save_format", ("HEIF",))
def test_pillow_pixel_aspect_ratio_multiframe(save_format):
    im1 = Image.effect_mandelbrot((64, 64), (-3, -2.5, 2, 2.5), 100)
    im1.info["pixel_aspect_ratio"] = (2, 1)
    im2 = Image.effect_mandelbrot((32, 32), (-3, -2.5, 2, 2.5), 100)
    im2.info["pixel_aspect_ratio"] = (3, 1)
    out_buf = BytesIO()
    im1.save(out_buf, format=save_format, save_all=True, append_images=[im2])
    heif_out = pillow_heif.open_heif(out_buf)
    assert heif_out[0].info["pixel_aspect_ratio"] == (2, 1)
    assert heif_out[1].info["pixel_aspect_ratio"] == (3, 1)
