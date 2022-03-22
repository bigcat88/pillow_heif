"""
Enums from libheif that can be used.
"""

from enum import IntEnum


class HeifChroma(IntEnum):
    """Chroma subsampling definitions."""

    UNDEFINED = 99
    """Undefined chroma."""
    MONOCHROME = 0
    """Mono chroma."""
    CHROMA_420 = 1
    """Cb and Cr are each subsampled at a factor of 2 both horizontally and vertically."""
    CHROMA_422 = 2
    """The two chroma components are sampled at half the horizontal sample rate of luma."""
    CHROMA_444 = 3
    """Each of the three Y'CbCr components has the same sample rate."""
    INTERLEAVED_RGB = 10
    """Simple interleaved RGB."""
    INTERLEAVED_RGBA = 11
    """Interleaved RGB with Alpha channel."""
    INTERLEAVED_RRGGBB_BE = 12
    """10 bit RGB BE."""
    INTERLEAVED_RRGGBBAA_BE = 13
    """10 bit RGB BE with Alpha channel."""
    INTERLEAVED_RRGGBB_LE = 14
    """10 bit RGB LE."""
    INTERLEAVED_RRGGBBAA_LE = 15
    """10 bit RGB LE with Alpha channel."""


class HeifColorspace(IntEnum):
    """Colorspace format of the image."""

    UNDEFINED = 99
    """Undefined colorspace."""
    YCBCR = 0
    """https://en.wikipedia.org/wiki/YCbCr"""
    RGB = 1
    """RGB colorspace."""
    MONOCHROME = 2
    """Monochrome colorspace."""


class HeifChannel(IntEnum):
    """Type of color channel."""

    Y = 0
    """Luma component"""
    CB = 1
    """Blue difference"""
    CR = 2
    """Red difference"""
    R = 3
    """Red color channel"""
    G = 4
    """Green color channel"""
    B = 5
    """Blue color channel"""
    ALPHA = 6
    """Alpha color channel"""
    INTERLEAVED = 10
    """Interleaved color channels"""


def encode_fourcc(fourcc):
    return ord(fourcc[0]) << 24 | ord(fourcc[1]) << 16 | ord(fourcc[2]) << 8 | ord(fourcc[3])


class HeifColorProfileType(IntEnum):
    """
    Color profile type definitions.
    If there is an ICC profile and an NCLX profile, the ICC profile prioritized.
    """

    NOT_PRESENT = 0
    """There is no color profile."""
    NCLX = encode_fourcc("nclx")
    """ISO/IEC 29199-2:2020"""
    RICC = encode_fourcc("rICC")
    """Restricted ICC. ISO/IEC 14496-12:2022"""
    PROF = encode_fourcc("prof")
    """Usual ICC profile."""


class HeifFiletype(IntEnum):
    """Result of `check_heif` function."""

    NO = 0
    """it is unsupported file"""
    YES_SUPPORTED = 1
    """it is heif and can be read by libheif"""
    YES_UNSUPPORTED = 2
    """it is heif, but probably cannot be read by libheif"""
    MAYBE = 3
    """not sure whether it is heif and is it supported"""


class HeifBrand(IntEnum):
    """Possible heif brands."""

    UNKNOWN = 0
    """unknown brand"""
    HEIC = 1
    """the usual HEIF images"""
    HEIX = 2
    """10bit images, or anything that uses h265 with range extension"""
    HEVC = 3
    """brand for image sequences"""
    HEVX = 4
    """brand for 10bit image sequences"""
    HEIM = 5
    """multiview"""
    HEIS = 6
    """scalable"""
    HEVM = 7
    """multiview sequence"""
    HEVS = 8
    """scalable sequence"""
    MIF1 = 9
    """image, any coding algorithm"""
    MSF1 = 10
    """sequence, any coding algorithm"""
    AVIF = 11
    """Avif image"""
    AVIS = 12
    """Avif sequence"""


class HeifErrorCode(IntEnum):
    """Possible libheif errors code."""

    OK = 0
    """Everything ok, no error occurred."""
    INPUT_DOES_NOT_EXIST = 1
    """Input file does not exist."""
    INVALID_INPUT = 2
    """Error in input file. Corrupted or invalid content."""
    UNSUPPORTED_FILETYPE = 3
    """Input file type is not supported."""
    UNSUPPORTED_FEATURE = 4
    """Image requires an unsupported decoder feature."""
    USAGE_ERROR = 5
    """Library API has been used in an invalid way."""
    MEMORY_ALLOCATION_ERROR = 6
    """Could not allocate enough memory."""
    DECODER_PLUGIN_ERROR = 7
    """The decoder plugin generated an error."""
    ENCODER_PLUGIN_ERROR = 8
    """The encoder plugin generated an error."""
    ENCODING_ERROR = 9
    """Error during encoding or when writing to the output."""
    COLOR_PROFILE_DOES_NOT_EXIST = 10
    """Application has asked for a color profile type that does not exist."""


class HeifCompressionFormat(IntEnum):
    """Possible HEIF compression formats."""

    UNDEFINED = 0
    """The compression format is not defined."""
    HEVC = 1
    """The compression format is HEVC."""
    AVC = 2
    """The compression format is AVC."""
    JPEG = 3
    """The compression format is JPEG."""
    AV1 = 4
    """The compression format is AV1."""


# --------------------------------------------------------------------
# DEPRECATED CONSTANTS.
# pylint: disable=invalid-name

heif_filetype_no = 0
heif_filetype_yes_supported = 1
heif_filetype_yes_unsupported = 2
heif_filetype_maybe = 3
