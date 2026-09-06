from io import BytesIO
from pathlib import Path
from unittest import mock

import pytest
from helpers import assert_image_equal, compare_hashes, gradient_rgb, hevc_enc
from PIL import Image, ImageSequence

import pillow_heif

pillow_heif.register_heif_opener()


def test_heif_thumbnails_present():
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    assert heif_file[0].info["thumbnails"] == [32, 16]
    assert heif_file[1].info["thumbnails"] == [32]
    assert len(heif_file[2].info["thumbnails"]) == 0


def test_pillow_thumbnails_present():
    for i, img in enumerate(ImageSequence.Iterator(Image.open(Path("images/heif/zPug_3.heic")))):
        if i == 0:
            assert img.info["thumbnails"] == [32, 16]
        elif i == 1:
            assert img.info["thumbnails"] == [32]
        else:
            assert len(img.info["thumbnails"]) == 0


def test_heif_to_pillow_thumbnails():
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    assert heif_file[0].to_pillow().info["thumbnails"] == [32, 16]
    assert heif_file[1].to_pillow().info["thumbnails"] == [32]
    assert len(heif_file[2].to_pillow().info["thumbnails"]) == 0


def test_from_pillow_thumbnails():
    for i, img in enumerate(ImageSequence.Iterator(Image.open(Path("images/heif/zPug_3.heic")))):
        if i == 0:
            assert pillow_heif.from_pillow(img).info["thumbnails"] == [32, 16]
        elif i == 1:
            assert pillow_heif.from_pillow(img).info["thumbnails"] == [32]
        else:
            assert len(pillow_heif.from_pillow(img).info["thumbnails"]) == 0


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
def test_heif_remove_thumbnails():
    buf = BytesIO()
    heif_file = pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))
    heif_file[0].info.pop("thumbnails")
    heif_file[1].info.pop("thumbnails")
    heif_file.save(buf)
    heif_file = pillow_heif.open_heif(buf)
    assert len(heif_file[0].info["thumbnails"]) == 0
    assert len(heif_file[1].info["thumbnails"]) == 0
    assert len(heif_file[2].info["thumbnails"]) == 0


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
def test_pillow_remove_thumbnails():
    buf = BytesIO()
    im = Image.open(Path("images/heif/zPug_3.heic"))
    ImageSequence.Iterator(im)[0].info.pop("thumbnails")
    ImageSequence.Iterator(im)[1].info.pop("thumbnails")
    im.save(buf, format="HEIF", save_all=True)
    for _, img in enumerate(ImageSequence.Iterator(Image.open(buf))):
        assert len(img.info["thumbnails"]) == 0


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize(
    "thumbs,result",
    (
        ([-1], []),
        ([0], []),
        ([1], []),
        ([100], []),
        ([200], []),
        ([28], [28]),
        ([96], [96]),
        ([28, 56], [28, 56]),
        ([0, 84], [84]),
        ([-1, 84, 0], [84]),
    ),
)
def test_heif_add_thumbs(thumbs, result):
    output = BytesIO()
    heif_file = pillow_heif.open_heif(Path("images/heif/L_8__29x100.heif"))
    heif_file.info["thumbnails"] = thumbs
    heif_file.save(output, quality=10)
    out_heif = pillow_heif.open_heif(output)
    assert out_heif.info["thumbnails"] == result


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
@pytest.mark.parametrize(
    "thumbs,result",
    (
        ([-1], []),
        ([0], []),
        ([1], []),
        ([100], []),
        ([200], []),
        ([28], [28]),
        ([96], [96]),
        ([28, 56], [28, 56]),
        ([0, 84], [84]),
        ([-1, 84, 0], [84]),
    ),
)
def test_pillow_add_thumbs(thumbs, result):
    output = BytesIO()
    im = Image.open(Path("images/heif/L_8__29x100.heif"))
    im.info["thumbnails"] = thumbs
    im.save(output, format="HEIF", quality=10)
    out_heif = Image.open(output)
    assert out_heif.info["thumbnails"] == result


def test_heif_get_thumbnail():
    heif_file = pillow_heif.open_heif(Path("images/heif_other/arrow.heic"))
    thumbnail = heif_file[0].get_thumbnail(0)
    assert isinstance(thumbnail, pillow_heif.HeifThumbnail)
    assert (thumbnail.size, thumbnail.mode) == ((240, 320), "RGB")
    assert thumbnail.info["bit_depth"] == 8
    assert thumbnail.info["chroma"] == 420
    assert thumbnail.info["icc_profile_type"] == "prof"
    assert len(thumbnail.data) == thumbnail.stride * 320
    pil_thumbnail = thumbnail.to_pillow()
    assert pil_thumbnail.info["icc_profile"] == thumbnail.info["icc_profile"]
    compare_hashes([heif_file[0].to_pillow().resize(thumbnail.size), pil_thumbnail], hash_size=8, max_difference=6)
    with pytest.raises(IndexError):
        heif_file[0].get_thumbnail(1)
    with pytest.raises(IndexError):
        heif_file[0].get_thumbnail(-1)
    assert pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))[1].get_thumbnail(0).mode == "L"


@pytest.mark.parametrize(
    "img_path,index,sizes",
    (
        ("images/heif/zPug_3.heic", 0, [(32, 32), (16, 16)]),
        ("images/heif/zPug_3.heic", 1, [(32, 32)]),
        ("images/heif/zPug_3.heic", 2, []),
        ("images/heif_other/empty_icc.heic", 1, [(114, 128)]),
        ("images/heif_other/nokia/stereo_1200x800.heic", 1, [(480, 320)]),
        ("images/heif_special/aux_YCbCr.heic", 0, [(512, 236)]),
    ),
)
def test_heif_thumbnail_sizes(img_path, index, sizes):
    image = pillow_heif.open_heif(Path(img_path))[index]
    thumbnails = [image.get_thumbnail(i) for i in range(len(image.info["thumbnails"]))]
    assert [i.size for i in thumbnails] == sizes
    assert [max(i.size) for i in thumbnails] == image.info["thumbnails"]
    for thumbnail in thumbnails:
        assert len(thumbnail.data) == thumbnail.stride * thumbnail.size[1]
        if max(thumbnail.size) >= 100:
            compare_hashes(
                [image.to_pillow().resize(thumbnail.size), thumbnail.to_pillow()], hash_size=8, max_difference=6
            )
    with pytest.raises(IndexError):
        image.get_thumbnail(len(thumbnails))


def test_heif_get_thumbnail_not_from_file():
    heif_file = pillow_heif.from_pillow(ImageSequence.Iterator(Image.open(Path("images/heif/zPug_3.heic")))[0])
    assert heif_file[0].info["thumbnails"] == [32, 16]
    with pytest.raises(IndexError):
        heif_file[0].get_thumbnail(0)


@pytest.mark.skipif(not hevc_enc(), reason="Requires HEVC encoder.")
def test_heif_thumbnail_roundtrip():
    im = gradient_rgb()
    buf = BytesIO()
    pillow_heif.from_pillow(im).save(buf, quality=90, thumbnails=[64, 32])
    image = pillow_heif.open_heif(buf)[0]
    assert image.info["thumbnails"] == [64, 32]
    thumbnail = image.get_thumbnail(0)
    assert (max(thumbnail.size), thumbnail.mode) == (64, "RGB")
    compare_hashes([im.resize(thumbnail.size), thumbnail.to_pillow()], hash_size=8, max_difference=6)
    assert max(image.get_thumbnail(1).size) == 32


def test_pillow_draft():
    im = Image.open(Path("images/heif_other/arrow.heic"))
    assert im.draft(None, (100, 100)) == ("RGB", (0, 0, 240, 320))
    assert (im.size, im.mode) == ((240, 320), "RGB")
    assert im.draft(None, (50, 50)) is None
    assert_image_equal(im, pillow_heif.open_heif(Path("images/heif_other/arrow.heic"))[0].get_thumbnail(0).to_pillow())
    assert im.info["thumbnails"] == [320]
    assert "exif" in im.info
    assert im.draft(None, (100, 100)) is None


@pytest.mark.parametrize(
    "img_path,size",
    (
        ("images/heif_other/arrow.heic", (300, 300)),
        ("images/heif_other/invalid_id.heic", (10, 10)),
        ("images/heif/L_8__29x100.heif", (10, 10)),
    ),
)
def test_pillow_draft_not_applicable(img_path, size):
    im = Image.open(Path(img_path))
    original_size = im.size
    assert im.draft(None, size) is None
    assert im.size == original_size
    im.load()
    assert im.size == original_size


def test_pillow_draft_frames():
    im = Image.open(Path("images/heif/zPug_3.heic"))
    im.seek(1)
    assert im.draft(None, (16, 16)) == ("L", (0, 0, 32, 32))
    im.load()
    assert_image_equal(im, pillow_heif.open_heif(Path("images/heif/zPug_3.heic"))[1].get_thumbnail(0).to_pillow())
    im.seek(0)
    assert im.size == (64, 64)
    assert im.draft(None, (8, 8)) == ("RGB", (0, 0, 16, 16))
    im.load()
    assert im.size == (16, 16)
    im.seek(2)
    assert im.draft(None, (8, 8)) is None
    assert im.size == (96, 64)


def test_pillow_draft_broken_thumbnail():
    with pytest.raises(EOFError):
        pillow_heif.open_heif(Path("images/heif_special/broken_thumbnail.heic"))[0].get_thumbnail(1).load()
    im = Image.open(Path("images/heif_special/broken_thumbnail.heic"))
    assert im.draft(None, (40, 40)) == ("RGB", (0, 0, 64, 64))
    im.load()
    assert im.size == (64, 64)


def test_pillow_draft_thumbnails_disabled():
    try:
        pillow_heif.options.THUMBNAILS = False
        im = Image.open(Path("images/heif_other/arrow.heic"))
        assert im.info["thumbnails"] == []
        assert im.draft(None, (100, 100)) is None
    finally:
        pillow_heif.options.THUMBNAILS = True


def test_pillow_draft_200mp():
    max_image_pixels = Image.MAX_IMAGE_PIXELS
    try:
        Image.MAX_IMAGE_PIXELS = None
        im = Image.open(Path("images/heif_special/200MP.heic"))
        assert im.draft(None, (256, 256)) == ("RGB", (0, 0, 384, 512))
        im.load()
        assert im.size == (384, 512)
    finally:
        Image.MAX_IMAGE_PIXELS = max_image_pixels


def _spy_thumbnail_selection(selections: list):
    original = pillow_heif.as_plugin._thumbnail_for_size  # pylint: disable=protected-access

    def selection(image, size):
        selections.append((size, original(image, size)))
        return selections[-1][1]

    return mock.patch("pillow_heif.as_plugin._thumbnail_for_size", selection)


def test_pillow_thumbnail_uses_embedded():
    selections: list = []
    with _spy_thumbnail_selection(selections):
        im = Image.open(Path("images/heif_other/arrow.heic"))
        im.thumbnail((100, 100))
    assert selections[0][0] == (200, 200)
    assert selections[0][1].size == (240, 320)
    assert im.size == (75, 100)
    im_full = Image.open(Path("images/heif_other/arrow.heic"))
    im_full.thumbnail((100, 100), reducing_gap=None)
    compare_hashes([im, im_full], hash_size=8, max_difference=6)


def test_pillow_thumbnail_reducing_gap():
    selections: list = []
    with _spy_thumbnail_selection(selections):
        im = Image.open(Path("images/heif_other/arrow.heic"))
        im.thumbnail((200, 200))
        assert selections[-1] == ((400, 400), None)
        im = Image.open(Path("images/heif_other/arrow.heic"))
        im.thumbnail((200, 200), reducing_gap=1.0)
        assert selections[-1][0] == (200, 200)
        assert selections[-1][1].size == (240, 320)
    assert im.size == (150, 200)


def test_pillow_thumbnail_undecodable_thumbnails():
    # the thumbnails of this file cannot be decoded by libheif 1.22+, the full image is used
    im = Image.open(Path("images/heif_other/cat.hif"))
    im.thumbnail((100, 100))
    assert im.size == (100, 67)
