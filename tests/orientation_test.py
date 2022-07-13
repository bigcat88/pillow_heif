import os
from io import BytesIO

import pytest
from packaging.version import parse as parse_version
from PIL import Image, ImageMath, ImageOps
from PIL import __version__ as pil_version

import pillow_heif

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pillow_heif.register_heif_opener()


def assert_image_equal(a, b):
    assert a.mode == b.mode
    assert a.size == b.size
    assert a.tobytes() == b.tobytes()


def convert_to_comparable(a, b):
    new_a, new_b = a, b
    if a.mode == "P":
        new_a = Image.new("L", a.size)
        new_b = Image.new("L", b.size)
        new_a.putdata(a.getdata())
        new_b.putdata(b.getdata())
    elif a.mode == "I;16":
        new_a = a.convert("I")
        new_b = b.convert("I")
    return new_a, new_b


def assert_image_similar(a, b, epsilon=0):
    assert a.mode == b.mode
    assert a.size == b.size
    a, b = convert_to_comparable(a, b)
    diff = 0
    for ach, bch in zip(a.split(), b.split()):
        ch_diff = ImageMath.eval("abs(a - b)", a=ach, b=bch).convert("L")
        diff += sum(i * num for i, num in enumerate(ch_diff.histogram()))
    ave_diff = diff / (a.size[0] * a.size[1])
    assert epsilon >= ave_diff


@pytest.mark.parametrize("orientation", (1, 2, 3, 4, 5, 6, 7, 8))
def test_jpeg_exif_orientation(orientation):
    im = Image.effect_mandelbrot((256, 128), (-3, -2.5, 2, 2.5), 100).crop((0, 0, 256, 96))
    im = im.convert(mode="RGB")
    exif_data = im.getexif()
    exif_data[0x0112] = orientation
    out_im = BytesIO()
    im.save(out_im, format="JPEG", exif=exif_data.tobytes())
    im = Image.open(out_im)
    # We are testing next two lines. They are equal to `save+open` operations.
    im_heif = pillow_heif.from_pillow(im)
    im_heif = im_heif[0].to_pillow()
    transposed_im = ImageOps.exif_transpose(im)
    assert_image_similar(transposed_im, im_heif)
    if orientation > 1:
        with pytest.raises(AssertionError):
            assert_image_similar(im, im_heif)


@pytest.mark.skipif(parse_version(pil_version) < parse_version("8.3.0"), reason="Requires Pillow >= 8.3")
@pytest.mark.parametrize("orientation", (1, 2, 3, 4, 5, 6, 7, 8))
def test_png_xmp_orientation(orientation):
    im = Image.effect_mandelbrot((256, 128), (-3, -2.5, 2, 2.5), 100).crop((0, 0, 256, 96))
    im = im.convert(mode="RGB")
    xmp = (
        '<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="XMP Core 5.4.0">\n'
        ' <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
        '  <rdf:Description rdf:about=""\n'
        '    xmlns:exif="http://ns.adobe.com/exif/1.0/"\n'
        '    xmlns:tiff="http://ns.adobe.com/tiff/1.0/"\n'
        '   tiff:Orientation="'
        + str(orientation)
        + '"/>\n </rdf:RDF>\n</x:xmpmeta>\n<?xpacket end="r"?>'
    )
    im.info["XML:com.adobe.xmp"] = xmp
    # We are testing next two lines. They are equal to `save+open` operations.
    im_heif = pillow_heif.from_pillow(im)
    im_heif = im_heif[0].to_pillow()
    assert im_heif.info["xmp"]
    assert isinstance(im_heif.info["xmp"], bytes)
    transposed_im = ImageOps.exif_transpose(im)
    assert_image_similar(transposed_im, im_heif)
    if orientation > 1:
        with pytest.raises(AssertionError):
            assert_image_similar(im, im_heif)


@pytest.mark.skipif(not pillow_heif.options().hevc_enc, reason="Requires HEIF encoder.")
@pytest.mark.parametrize("orientation", (1, 2, 3, 4, 5, 6, 7, 8))
def test_heif_exif_orientation(orientation):
    im = Image.effect_mandelbrot((256, 128), (-3, -2.5, 2, 2.5), 100).crop((0, 0, 256, 96))
    im = im.convert(mode="RGB")
    out_im_heif = BytesIO()
    exif_data = im.getexif()
    exif_data[0x0112] = orientation
    im.save(out_im_heif, format="HEIF", exif=exif_data.tobytes(), quality=-1)
    im_heif = Image.open(out_im_heif)
    assert im_heif.info["original_orientation"] == orientation
    # We should ignore all EXIF rotation flags for HEIF
    assert_image_similar(im, im_heif)


@pytest.mark.skipif(not pillow_heif.options().hevc_enc, reason="Requires HEIF encoder.")
@pytest.mark.parametrize("orientation", (1, 2, 3, 4, 5, 6, 7, 8))
def test_heif_xmp_orientation(orientation):
    im = Image.effect_mandelbrot((256, 128), (-3, -2.5, 2, 2.5), 100).crop((0, 0, 256, 96))
    im = im.convert(mode="RGB")
    xmp = (
        '<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="XMP Core 5.4.0">\n'
        ' <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
        '  <rdf:Description rdf:about=""\n'
        '    xmlns:exif="http://ns.adobe.com/exif/1.0/"\n'
        '    xmlns:tiff="http://ns.adobe.com/tiff/1.0/"\n'
        '   tiff:Orientation="'
        + str(orientation)
        + '"/>\n </rdf:RDF>\n</x:xmpmeta>\n<?xpacket end="r"?>'
    )
    out_im_heif = BytesIO()
    im.save(out_im_heif, format="HEIF", xmp=xmp.encode("utf-8"), quality=-1)
    im_heif = Image.open(out_im_heif)
    assert im_heif.info["original_orientation"] == orientation
    # We should ignore all EXIF rotation flags for HEIF
    assert_image_similar(im, im_heif)
