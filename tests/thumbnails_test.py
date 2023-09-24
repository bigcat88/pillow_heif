from io import BytesIO
from pathlib import Path

import pytest
from helpers import hevc_enc
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
