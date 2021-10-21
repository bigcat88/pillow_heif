from .constants import *
from .reader import *
from .writer import *
from .error import HeifError
from . import _libheif

from PIL import Image, ImageFile


__version__ = "0.1.3"


def libheif_version():
    return _libheif.ffi.string(_libheif.lib.heif_get_version()).decode()


class HeifImageFile(ImageFile.ImageFile):
    format = "HEIF"
    format_description = "HEIF/HEIC image"

    def _open(self):
        data = self.fp.read(16)
        if not check_heif_magic(data):
            raise SyntaxError("not a HEIF file")
        self.fp.seek(0)
        try:
            heif_file = read(self.fp)
        except HeifError as e:
            raise SyntaxError(str(e))

        # size in pixels (width, height)
        self._size = heif_file.size

        # mode setting
        self.mode = heif_file.mode

        # Add Exif
        if heif_file.metadata:
            for data in heif_file.metadata:
                if data["type"] == "Exif":
                    self.info["exif"] = data["data"]
                    break

        # Add Color Profile
        if heif_file.color_profile:
            if heif_file.color_profile["type"] != "unknown":
                self.color_profile = heif_file.color_profile
        offset = self.fp.tell()
        self.tile = [("heif", (0, 0) + self.size, offset, (heif_file,))]


class HeifDecoder(ImageFile.PyDecoder):
    _pulls_fd = True

    def decode(self, buffer):
        heif_file = self.args[0]
        mode = heif_file.mode
        raw_decoder = Image._getdecoder(mode, "raw", (mode, heif_file.stride))
        raw_decoder.setimage(self.im)
        return raw_decoder.decode(heif_file.data)


def check_heif_magic(data):
    magic1 = data[4:8]
    magic2 = data[8:12]
    # https://github.com/strukturag/libheif/issues/83
    # https://github.com/GNOME/gimp/commit/e4bff4c8016f18195f9a6229f59cbf41740ddb8d
    # 'heic': the usual HEIF images
    # 'heix': 10bit images, or anything that uses h265 with range extension
    # 'hevc', 'hevx': brands for image sequences
    # 'heim': multiview
    # 'heis': scalable
    # 'hevm': multiview sequence
    # 'hevs': scalable sequence
    # 'hevs': scalable sequence
    code_list = [
        # Other
        b"heic",
        b"heix",
        b"hevc",
        b"hevx",
        b"heim",
        b"heis",
        b"hevm",
        b"hevs",
        # iPhone
        b"mif1",
    ]
    return magic1 == b"ftyp" or magic2 in code_list


def register_heif_opener():
    Image.register_open(HeifImageFile.format, HeifImageFile, check_heif_magic)
    Image.register_decoder("heif", HeifDecoder)
    Image.register_extensions(HeifImageFile.format, [".heic", ".heif"])
    Image.register_mime(HeifImageFile.format, "image/heif")
