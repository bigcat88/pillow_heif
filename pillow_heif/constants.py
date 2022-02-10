"""
Constants from libheif that is used by pillow_heif.
"""


# pylint: disable=invalid-name
heif_chroma_undefined = 99
heif_chroma_monochrome = 0
heif_chroma_420 = 1
heif_chroma_422 = 2
heif_chroma_444 = 3
heif_chroma_interleaved_RGB = 10
heif_chroma_interleaved_RGBA = 11
heif_chroma_interleaved_RRGGBB_BE = 12
heif_chroma_interleaved_RRGGBBAA_BE = 13
heif_chroma_interleaved_RRGGBB_LE = 14
heif_chroma_interleaved_RRGGBBAA_LE = 15

heif_colorspace_undefined = 99
heif_colorspace_YCbCr = 0
heif_colorspace_RGB = 1
heif_colorspace_monochrome = 2

heif_channel_Y = 0
heif_channel_Cb = 1
heif_channel_Cr = 2
heif_channel_R = 3
heif_channel_G = 4
heif_channel_B = 5
heif_channel_Alpha = 6
heif_channel_interleaved = 10


def encode_fourcc(fourcc):
    encoded = ord(fourcc[0]) << 24 | ord(fourcc[1]) << 16 | ord(fourcc[2]) << 8 | ord(fourcc[3])
    return encoded


heif_color_profile_type_not_present = 0
heif_color_profile_type_nclx = encode_fourcc("nclx")
heif_color_profile_type_rICC = encode_fourcc("rICC")
heif_color_profile_type_prof = encode_fourcc("prof")

heif_filetype_no = 0
heif_filetype_yes_supported = 1
heif_filetype_yes_unsupported = 2
heif_filetype_maybe = 3

heif_brand_unknown_brand = 0
heif_brand_heic = 1
heif_brand_heix = 2
heif_brand_hevc = 3
heif_brand_hevx = 4
heif_brand_heim = 5
heif_brand_heis = 6
heif_brand_hevm = 7
heif_brand_hevs = 8
heif_brand_mif1 = 9
heif_brand_msf1 = 10
heif_brand_avif = 11
heif_brand_avis = 12
