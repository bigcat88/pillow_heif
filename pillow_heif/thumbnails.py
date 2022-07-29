"""Functions for work with thumbnails."""

from typing import List, Union

from PIL import Image

from .as_opener import _LibHeifImageFile
from .heif import HeifFile, HeifImage, HeifThumbnail
from .private import HeifCtxAsDict


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
    elif isinstance(im, _LibHeifImageFile):
        thumb = _choose_thumbnail(im.info.get("thumbnails", []), min_box)
        if thumb:
            thumb = thumb.to_pillow()
    return thumb if thumb else im


def add_thumbnails(im: Union[HeifFile, HeifImage, Image.Image], boxes: Union[List[int], int]) -> None:
    """Add thumbnail(s) to an image(s).

    .. note:: Method creates thumbnails without image data, they will be encoded during `save` operation.

    :param im: For ``HeifFile`` will add thumbnail(s) to all images in it.
        For ``HeifImage`` or a Pillow image it will add thumbnails only to specified image.
    :param boxes: int or list of ints determining size of thumbnail(s) to generate for image.

    :returns: None"""

    if isinstance(im, HeifFile):
        for i in im:
            _add_thumbnails(i, boxes)
    else:
        _add_thumbnails(im, boxes)


def _add_thumbnails(im: Union[HeifImage, Image.Image], boxes: Union[List[int], int]) -> None:
    if isinstance(boxes, list):
        boxes_list = boxes
    else:
        boxes_list = [boxes]
    for box in boxes_list:
        if box <= 3:
            continue
        if im.size[0] <= box and im.size[1] <= box:
            continue
        if im.size[0] > im.size[1]:
            thumb_height = int(im.size[1] * box / im.size[0])
            thumb_width = box
        else:
            thumb_width = int(im.size[0] * box / im.size[1])
            thumb_height = box
        thumb_height = thumb_height - 1 if (thumb_height & 1) else thumb_height
        thumb_width = thumb_width - 1 if (thumb_width & 1) else thumb_width
        thumbnails = im.thumbnails if isinstance(im, HeifImage) else im.info.get("thumbnails", [])
        if max((thumb_height, thumb_width)) in [max(i.size) for i in thumbnails]:
            continue
        __heif_ctx = HeifCtxAsDict(im.mode, (thumb_width, thumb_height), None, stride=0)
        if isinstance(im, HeifImage):
            im.thumbnails.append(HeifThumbnail(__heif_ctx, im))
        else:
            if im.info.get("thumbnails", None) is None:
                im.info["thumbnails"] = [HeifThumbnail(__heif_ctx, __heif_ctx)]
            else:
                im.info["thumbnails"].append(HeifThumbnail(__heif_ctx, __heif_ctx))


def _choose_thumbnail(thumbnails: list, min_box: int):
    for thumb in thumbnails:
        if thumb.size[0] >= min_box or thumb.size[1] >= min_box:
            if thumb.data:
                return thumb
    return None
