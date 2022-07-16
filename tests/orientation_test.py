from io import BytesIO

import pytest
from helpers import assert_image_similar
from packaging.version import parse as parse_version
from PIL import Image, ImageOps
from PIL import __version__ as pil_version

import pillow_heif

pillow_heif.register_heif_opener()


@pytest.mark.skipif(not pillow_heif.options().hevc_enc, reason="Requires HEIF encoder.")
@pytest.mark.skipif(parse_version(pil_version) < parse_version("8.3.0"), reason="Requires Pillow >= 8.3")
@pytest.mark.parametrize("orientation", (1, 2, 3, 4, 5, 6, 7, 8))
@pytest.mark.parametrize("im_format", ("JPEG", "PNG"))
def test_exif_orientation(orientation, im_format):
    out_im = BytesIO()
    out_heif_im = BytesIO()
    im = Image.effect_mandelbrot((256, 128), (-3, -2.5, 2, 2.5), 100).crop((0, 0, 256, 96))
    im = im.convert(mode="RGB")
    exif_data = Image.Exif()
    exif_data[0x0112] = orientation
    im.save(out_im, format=im_format, exif=exif_data.tobytes())
    im = Image.open(out_im)
    assert im.getexif()[0x0112] == orientation
    # Saving image with EXIF to HEIF
    im.save(out_heif_im, format="HEIF", quality=-1)
    im_heif = Image.open(out_heif_im)
    im_heif_exif = im_heif.getexif()
    assert 0x0112 not in im_heif_exif or im_heif_exif[0x0112] == 1
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
    exif_data = Image.Exif()
    exif_data[0x0112] = orientation
    im.save(out_im_heif, format="HEIF", exif=exif_data.tobytes(), quality=-1)
    im_heif = Image.open(out_im_heif)
    # We should ignore all EXIF rotation flags for HEIF
    assert im_heif.info["original_orientation"] == orientation
    im_heif_exif = im_heif.getexif()
    assert 0x0112 not in im_heif_exif or im_heif_exif[0x0112] == 1
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
    # We should ignore all XMP rotation flags for HEIF
    assert im_heif.info["original_orientation"] == orientation
    assert_image_similar(im, im_heif)


@pytest.mark.skipif(not pillow_heif.options().hevc_enc, reason="Requires HEIF encoder.")
@pytest.mark.skipif(parse_version(pil_version) < parse_version("8.3.0"), reason="Requires Pillow >= 8.3")
@pytest.mark.parametrize("orientation", (1, 2))
@pytest.mark.parametrize("im_format", ("JPEG", "PNG"))
def test_exif_heif_exif_orientation(orientation, im_format):
    out_im = BytesIO()
    out_heif_im = BytesIO()
    im = Image.effect_mandelbrot((256, 128), (-3, -2.5, 2, 2.5), 100).crop((0, 0, 256, 96))
    im = im.convert(mode="RGB")
    exif_data = Image.Exif()
    exif_data[0x0112] = orientation
    im.save(out_im, format=im_format, exif=exif_data.tobytes())
    im = Image.open(out_im)
    assert im.getexif()[0x0112] == orientation
    # Saving image with EXIF to HEIF
    im.save(out_heif_im, format="HEIF", quality=-1, exif=exif_data.tobytes())
    im_heif = Image.open(out_heif_im)
    im_heif_exif = im_heif.getexif()
    assert 0x0112 not in im_heif_exif or im_heif_exif[0x0112] == 1
    transposed_im = ImageOps.exif_transpose(im)
    assert_image_similar(transposed_im, im_heif)
    if orientation > 1:
        with pytest.raises(AssertionError):
            assert_image_similar(im, im_heif)
