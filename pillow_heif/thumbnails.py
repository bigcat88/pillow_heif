"""Functions for work with thumbnails."""

from .as_opener import HeifImageFile
from .heif import HeifFile, HeifImage


def thumbnail(im, min_box: int = 0):
    """Returns a thumbnail with minimum specified box size or an original if there is no a thumbnail.

    .. note:: If you use it for a Pillow image, it ``should not be loaded`` before call.

    :param im: :py:class:`HeifImage`, :py:class:`HeifFile` or :external:py:class:`PIL.Image.Image` class.
    :param min_box: optional integer with minimum size of thumbnail's box size.

    :returns: Class with the same type the input parameter ``im`` has."""

    if isinstance(im, HeifFile):
        im = im.images[im.primary_index()]
    thumb = None
    if isinstance(im, HeifImage):
        thumb = _choose_thumbnail(im.thumbnails, min_box)
        if thumb:
            thumb.info = im.info
    elif isinstance(im, HeifImageFile):
        thumb = _choose_thumbnail(im.info.get("thumbnails", []), min_box)
        if thumb:
            thumb = thumb.to_pillow()
    return thumb if thumb else im


def _choose_thumbnail(thumbnails: list, min_box: int):
    for thumb in thumbnails:
        if thumb.size[0] >= min_box or thumb.size[1] >= min_box:
            if thumb.data:
                return thumb
    return None
