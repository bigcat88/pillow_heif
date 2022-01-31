from PIL import Image, ImageFile

from .reader import read
from .error import HeifError


class HeifImageFile(ImageFile.ImageFile):
    format = 'HEIF'
    format_description = 'HEIF/HEIC image'
    color_profile = None

    def _open(self):
        data = self.fp.read(16)
        if not check_heif_magic(data):
            raise SyntaxError('not a HEIF file')
        self.fp.seek(0)
        try:
            heif_file = read(self.fp)
        except HeifError as e:
            raise SyntaxError(str(e)) from None

        # size in pixels (width, height)
        self._size = heif_file.size

        # mode setting
        self.mode = heif_file.mode

        # Add Exif
        if heif_file.metadata:
            for data in heif_file.metadata:
                if data['type'] == 'Exif':
                    self.info['exif'] = data['data']
                    break

        # Add Color Profile
        if heif_file.color_profile:
            if heif_file.color_profile['type'] != 'unknown':
                self.color_profile = heif_file.color_profile
        offset = self.fp.tell()
        self.tile = [('heif', (0, 0) + self.size, offset, (heif_file,))]


class HeifDecoder(ImageFile.PyDecoder):
    _pulls_fd = True

    def decode(self, buffer):
        heif_file = self.args[0]
        mode = heif_file.mode
        raw_decoder = Image._getdecoder(mode, 'raw', (mode, heif_file.stride))
        raw_decoder.setimage(self.im)
        return raw_decoder.decode(heif_file.data)


def check_heif_magic(data) -> bool:
    # according to HEIF standard ISO/IEC 23008-12:2017
    # https://standards.iso.org/ittf/PubliclyAvailableStandards/c066067_ISO_IEC_23008-12_2017.zip
    if len(data) < 12:
        return False
    magic1 = data[4:8]
    if magic1 != b"ftyp":
        return False
    magic2 = data[8:12]
    code_list = [
        b"heic",  # the usual HEIF images
        b"heix",  # 10bit images, or anything that uses h265 with range extension
        b"hevc",  # image sequences
        b"hevx",  # image sequences
        b"heim",  # multiview
        b"heis",  # scalable
        b"hevm",  # multiview sequence
        b"hevs",  # scalable sequence
        b"mif1",  # image, any coding algorithm
        b"msf1",  # sequence, any coding algorithm
        # avif
        # avis
    ]
    return magic2 in code_list


def register_heif_opener():
    Image.register_open(HeifImageFile.format, HeifImageFile, check_heif_magic)
    Image.register_decoder('heif', HeifDecoder)
    Image.register_extensions(HeifImageFile.format, ['.heic', '.heif'])
    Image.register_mime(HeifImageFile.format, 'image/heif')
