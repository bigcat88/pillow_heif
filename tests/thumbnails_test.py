from gc import collect
from io import BytesIO

import pytest
from helpers import compare_hashes
from PIL import Image, ImageSequence

import pillow_heif

pillow_heif.register_heif_opener()
if not pillow_heif.options().hevc_enc:
    pytest.skip(reason="Requires HEIF encoder.", allow_module_level=True)


# Creating HEIF file in memory with 3 images.
# Second image is a Primary Image with EXIF and XMP data.
# First two images has 2 thumbnails each, third image has no thumbnails.
def create_thumbnail_heif(size):
    _ = Image.effect_mandelbrot(size, (-3, -2.5, 2, 2.5), 100)
    im_heif = pillow_heif.from_pillow(_)
    im_heif.add_from_pillow(_.crop((0, 0, 256, 256)))
    im_heif.add_thumbnails(boxes=[128, 64])
    im_heif.add_from_pillow(_.crop((0, 0, 192, 192)))
    _heif_buf = BytesIO()
    exif = Image.Exif()
    exif[0x010E] = "this is a desc"
    im_heif.save(_heif_buf, primary_index=1, exif=exif.tobytes(), xmp=xmp_data)
    return _heif_buf


xmp_data = b"xmp_data"
heif_buf = create_thumbnail_heif((512, 512))


def test_heif_enumerate_thumbnails():
    heif_file = pillow_heif.open_heif(heif_buf)
    assert len(list(heif_file.thumbnails_all())) == 4
    assert len(list(heif_file.thumbnails_all(one_for_image=True))) == 2


def test_heif_enumerate_thumbnails_data():
    heif_file = pillow_heif.open_heif(heif_buf)
    for thumbnail in heif_file.thumbnails_all():
        assert len(thumbnail.data)
    for thumbnail in heif_file.thumbnails_all(one_for_image=True):
        assert len(thumbnail.data)


def test_heif_thumbnail():
    for i, img in enumerate(pillow_heif.open_heif(heif_buf)):
        thumbnail = pillow_heif.thumbnail(img)
        if i == 2:
            assert thumbnail.size == img.size
            assert isinstance(thumbnail, pillow_heif.HeifImage)
        else:
            assert thumbnail.size != img.size
            assert isinstance(thumbnail, pillow_heif.HeifThumbnail)
        assert len(thumbnail.data)


def test_pillow_thumbnail():
    for i, img in enumerate(ImageSequence.Iterator(Image.open(heif_buf))):
        thumbnail = pillow_heif.thumbnail(img)
        assert isinstance(thumbnail, Image.Image)
        if i == 2:
            assert thumbnail.size == img.size
            assert isinstance(thumbnail.info.get("thumbnails"), list)
        else:
            assert thumbnail.size != img.size
            assert thumbnail.info.get("thumbnails", None) is None
        assert thumbnail.info["primary"] == bool(i == 1)
        assert len(thumbnail.tobytes())


def test_pillow_thumbnail_image_loaded():
    for i, img in enumerate(ImageSequence.Iterator(Image.open(heif_buf))):
        img.load()
        thumbnail = pillow_heif.thumbnail(img)
        assert isinstance(thumbnail, Image.Image)
        if i == 2:
            assert thumbnail.size == img.size
            assert isinstance(thumbnail.info.get("thumbnails"), list)
        else:
            assert thumbnail.size != img.size
            assert thumbnail.info.get("thumbnails", None) is None
        assert thumbnail.info["primary"] == bool(i == 1)
        assert len(thumbnail.tobytes())


def test_pillow_thumbnail_one_image_loaded():
    heif_buf_one_image = BytesIO()
    Image.open(heif_buf).save(heif_buf_one_image, format="HEIF")
    im = Image.open(heif_buf_one_image)
    thumbnail = pillow_heif.thumbnail(im)
    assert thumbnail.size != im.size
    assert thumbnail.info.get("thumbnails") is None
    im.load()
    thumbnail = pillow_heif.thumbnail(im)
    assert thumbnail.size == im.size
    assert isinstance(thumbnail.info.get("thumbnails"), list)


def test_heif_thumbnail_above_size():
    for img in pillow_heif.open_heif(heif_buf):
        thumbnail = pillow_heif.thumbnail(img, min_box=9999)
        assert thumbnail.size == img.size
        assert isinstance(thumbnail, pillow_heif.HeifImage)
        assert len(thumbnail.data)


def test_pillow_thumbnail_above_size():
    for img in ImageSequence.Iterator(Image.open(heif_buf)):
        thumbnail = pillow_heif.thumbnail(img, min_box=9999)
        assert thumbnail.size == img.size
        assert isinstance(thumbnail, Image.Image)
        assert isinstance(thumbnail.info.get("thumbnails"), list)


def test_heif_thumbnail_below_size():
    for i, img in enumerate(pillow_heif.open_heif(heif_buf)):
        thumbnail = pillow_heif.thumbnail(img, min_box=16)
        if i == 2:
            assert thumbnail.size == img.size
            assert isinstance(thumbnail, pillow_heif.HeifImage)
        else:
            assert thumbnail.size != img.size
            assert isinstance(thumbnail, pillow_heif.HeifThumbnail)
        assert len(thumbnail.data)


def test_pillow_thumbnail_below_size():
    for i, img in enumerate(ImageSequence.Iterator(Image.open(heif_buf))):
        thumbnail = pillow_heif.thumbnail(img, min_box=16)
        if i == 2:
            assert thumbnail.size == img.size
            assert isinstance(thumbnail.info.get("thumbnails"), list)
        else:
            assert thumbnail.size != img.size
            assert thumbnail.info.get("thumbnails", None) is None
        assert len(thumbnail.tobytes())


def test_heif_thumbnail_primary():
    # checking if `thumbnail` return Primary Image thumbnail when input is a heif_file
    heif_file = pillow_heif.open_heif(heif_buf)
    thumbnail = pillow_heif.thumbnail(heif_file)
    assert thumbnail == heif_file[1].thumbnails[0]


def test_heif_thumbnail_no_xmp_exif():
    thumbnail = pillow_heif.thumbnail(pillow_heif.open_heif(heif_buf)[0])
    assert not thumbnail.info["exif"]
    assert not thumbnail.info["xmp"]


def test_pillow_thumbnail_no_xmp_exif():
    thumbnail = pillow_heif.thumbnail(ImageSequence.Iterator(Image.open(heif_buf))[0])
    assert not thumbnail.info["exif"]
    assert not thumbnail.info["xmp"]


def test_heif_thumbnail_xmp_exif():
    thumbnail = pillow_heif.thumbnail(pillow_heif.open_heif(heif_buf))
    assert thumbnail.info["exif"]
    assert thumbnail.info["xmp"] == xmp_data


def test_pillow_thumbnail_xmp_exif():
    thumbnail = pillow_heif.thumbnail(Image.open(heif_buf))
    assert thumbnail.info["exif"]
    assert thumbnail.info["xmp"] == xmp_data
    assert isinstance(thumbnail.getexif(), Image.Exif)


def test_heif_thumbnail_references():
    heif_file = pillow_heif.open_heif(heif_buf)
    thumbnails_all = list(heif_file.thumbnails_all())
    assert thumbnails_all[0].get_original() == heif_file[0]
    assert thumbnails_all[1].get_original() == heif_file[0]
    assert thumbnails_all[2].get_original() == heif_file[1]
    assert thumbnails_all[3].get_original() == heif_file[1]
    del heif_file[0]
    collect()
    assert thumbnails_all[0].get_original() is None
    assert thumbnails_all[0].get_original() is None
    assert str(thumbnails_all[0]).find("Original:None") != -1
    assert thumbnails_all[2].get_original() == heif_file[0]
    assert thumbnails_all[3].get_original() == heif_file[0]
    pillow_img = heif_file[0].to_pillow()
    assert pillow_img.info["thumbnails"][0].get_original() is None
    assert pillow_img.info["thumbnails"][1].get_original() is None
    img_from_pillow = pillow_heif.from_pillow(pillow_img)
    assert img_from_pillow.thumbnails[0].get_original() == img_from_pillow[0]
    assert img_from_pillow.thumbnails[1].get_original() == img_from_pillow[0]
    assert str(img_from_pillow.thumbnails[0]).find("Original:None") == -1


@pytest.mark.parametrize(
    "thumbs,expected_after",
    (
        (-1, [2, 2, 0]),
        ([-1], [2, 2, 0]),
        (0, [2, 2, 0]),
        ([0], [2, 2, 0]),
        (1, [2, 2, 0]),
        ([1], [2, 2, 0]),
        (64, [2, 2, 1]),
        ([64], [2, 2, 1]),
        ([2048], [2, 2, 0]),
        (96, [3, 3, 1]),
        ([96], [3, 3, 1]),
        ([84, 0], [3, 3, 1]),
        ([0, 84], [3, 3, 1]),
        ([96, 84], [4, 4, 2]),
    ),
)
@pytest.mark.parametrize("way_to_add", ("HeifFile", "HeifImage"))
@pytest.mark.parametrize("heif_file_buf", (heif_buf, create_thumbnail_heif((417, 411))))
def test_add_thumbs(thumbs, expected_after, way_to_add, heif_file_buf):
    heif_file = pillow_heif.open_heif(heif_file_buf)
    if way_to_add == "HeifImage":
        heif_file[0].add_thumbnails(thumbs)
        heif_file[1].add_thumbnails(thumbs)
        heif_file[2].add_thumbnails(thumbs)
    else:
        heif_file.add_thumbnails(thumbs)
    output = BytesIO()
    heif_file.save(output, quality=-1)
    out_heif = pillow_heif.open_heif(output)
    for i in range(3):
        assert len(out_heif[i].thumbnails) == expected_after[i]
    compare_hashes([out_heif[0].to_pillow(), out_heif[0].thumbnails[0].to_pillow()], hash_size=8, max_difference=3)


def test_remove_thumbs():
    heif_file = pillow_heif.open_heif(heif_buf)
    del heif_file[0].thumbnails[0]
    out_buffer = BytesIO()
    heif_file.save(out_buffer)
    out_heif = pillow_heif.open_heif(out_buffer)
    assert len(out_heif[0].thumbnails) == 1
    assert len(out_heif[1].thumbnails) == 2
    assert len(out_heif[2].thumbnails) == 0
    heif_file = pillow_heif.open_heif(heif_buf)
    heif_file[1].thumbnails = []
    out_buffer = BytesIO()
    heif_file.save(out_buffer)
    out_heif = pillow_heif.open_heif(out_buffer)
    assert len(out_heif[0].thumbnails) == 2
    assert len(out_heif[1].thumbnails) == 0
    assert len(out_heif[2].thumbnails) == 0
