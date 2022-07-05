"""
Functions and classes for heif images to read and write.
"""

from copy import deepcopy
from typing import Any, Dict, Iterator, List, Union
from warnings import warn
from weakref import ref

from _pillow_heif_cffi import ffi, lib
from PIL import Image, ImageOps, ImageSequence

from ._libheif_ctx import LibHeifCtx, LibHeifCtxWrite
from ._options import options
from .constants import HeifChannel, HeifChroma, HeifColorspace, HeifFiletype
from .error import HeifError, HeifErrorCode, check_libheif_error
from .misc import _get_bytes, set_orientation
from .private import (
    FFI_DRY_ALLOC,
    MODE_CONVERT,
    MODE_INFO,
    HeifCtxAsDict,
    get_pure_stride,
    read_color_profile,
    read_metadata,
    retrieve_exif,
    retrieve_xmp,
    set_color_profile,
    set_exif,
    set_metadata,
    set_xmp,
)


class HeifImageBase:
    """Base class for :py:class:`HeifImage` and :py:class:`HeifThumbnail`"""

    size: tuple
    """Width and height of the image."""

    mode: str
    """A string which defines the type and depth of a pixel in the image:
    `Pillow Modes <https://pillow.readthedocs.io/en/stable/handbook/concepts.html#modes>`_
    For currently supported modes by Pillow-Heif see :ref:`image-modes`."""

    def __init__(self, heif_ctx: Union[LibHeifCtx, HeifCtxAsDict], handle, for_encoding=False):
        self._img_data: Dict[str, Any] = {}
        self._heif_ctx = heif_ctx
        if isinstance(heif_ctx, LibHeifCtx):
            self._handle = ffi.gc(handle, lib.heif_image_handle_release)
            self.size = (
                lib.heif_image_handle_get_width(self._handle),
                lib.heif_image_handle_get_height(self._handle),
            )
            self.mode = "RGBA" if bool(lib.heif_image_handle_has_alpha_channel(self._handle)) else "RGB"
            bit_depth = 8 if heif_ctx.to_8bit else lib.heif_image_handle_get_luma_bits_per_pixel(self._handle)
            if bit_depth > 8:
                self.mode += f";{bit_depth}"
        else:
            self._handle = None
            self.size = heif_ctx.size
            self.mode = heif_ctx.mode
            if heif_ctx.data:
                new_mode = MODE_INFO[self.mode][4] if for_encoding else None
                if isinstance(new_mode, tuple):
                    new_mode = new_mode[1] if options().save_to_12bit else new_mode[0]
                _img = self._create_image(heif_ctx.data, heif_ctx.stride, new_mode)
                self._img_to_img_data_dict(_img)

    @property
    def bit_depth(self):
        """Image channel pixel bit depth. Possible values: 8, 10, 12, 16

        .. note:: When ``convert_hdr_to_8bit`` is True, return value will be always ``8`` when
         image opened from file(e.g. was not created with ``from_pillow`` or ``add_from_*`` functions)."""

        return MODE_INFO[self.mode][1]

    @property
    def original_bit_depth(self):
        """Number of bits in colour channel, before it was decoded using ``convert_hdr_to_8bit`` parameter.

        .. note:: If ``convert_hdr_to_8bit`` is ``False`` then this field is always equal to ``bit_depth``

            This includes situations where image was created not from a file.

        :returns: An int value representing number of bits per color channel."""

        if self._handle is not None:
            return lib.heif_image_handle_get_luma_bits_per_pixel(self._handle)
        return self.bit_depth

    @property
    def has_alpha(self):
        """``True`` for images with ``alpha`` channel, ``False`` otherwise.

        :returns: "True" or "False" """

        return self.mode.find("A") != -1

    @property
    def heif_img(self):
        self._load_if_not()
        return self._img_data.get("img", None)

    @property
    def data(self):
        """Decodes image and returns image data from ``libheif``. See :ref:`image_data`

        .. note:: Actual size of data returned by ``data`` can be bigger then ``width * height * pixel size``.

        :returns: ``bytes`` of the decoded image from ``libheif``."""

        self._load_if_not()
        return self._img_data.get("data", None)

    @property
    def stride(self):
        """Decodes image and returns stride.

        :returns: ``int`` stride of the decoded image."""

        self._load_if_not()
        return self._img_data.get("stride", None)

    def convert_to(self, mode: str) -> None:
        """Decode and convert in place image to specified mode.

        :param mode: for list of supported conversions, see: :ref:`convert_to`

        :exception KeyError: If conversion between modes is not supported."""

        current_stride = self.stride
        current_data = bytes(self.data)  # copying `data` to bytes so it will not be GC collected.
        self.unload()
        _img = self._create_image(current_data, current_stride, mode)
        self._img_to_img_data_dict(_img)

    def to_pillow(self, ignore_thumbnails: bool = False) -> Image.Image:
        """Helper method to create :py:class:`PIL.Image.Image`

        :param ignore_thumbnails: Shall ``info["thumbnails"]`` be empty or not.

        :returns: :py:class:`PIL.Image.Image` class created from this image."""

        image = Image.frombytes(
            self.mode,  # noqa
            self.size,
            self.data,
            "raw",
            self.mode,
            self.stride,
        )
        if isinstance(self, HeifImage):
            for k in ("exif", "xmp", "metadata"):
                image.info[k] = self.info[k]
            for k in ("icc_profile", "icc_profile_type", "nclx_profile"):
                if k in self.info:
                    image.info[k] = self.info[k]
            image.info["thumbnails"] = [] if ignore_thumbnails else deepcopy(self.thumbnails)
            image.info["original_orientation"] = set_orientation(image.info)
        return image

    def load(self):
        """Decode image.

        Usually, you do not need to call this, image will be decoded automatically
        when accessing ``data`` or ``stride`` properties."""

        self._load_if_not()
        return self

    def unload(self):
        if self._handle is not None:
            self._img_data.clear()

    @property
    def __array_interface__(self):
        """Numpy array interface support"""

        shape = (self.size[1], self.size[0])
        if MODE_INFO[self.mode][0] > 1:
            shape += (MODE_INFO[self.mode][0],)
        typestr = MODE_INFO[self.mode][5]
        data = bytes(self._get_pure_data())
        return {"shape": shape, "typestr": typestr, "version": 3, "data": data}

    def _color(self) -> HeifColorspace:
        return MODE_INFO[self.mode][2]

    def _chroma(self) -> HeifChroma:
        return MODE_INFO[self.mode][3]

    def _channel(self) -> HeifChannel:
        return HeifChannel.Y if self._color() == HeifColorspace.MONOCHROME else HeifChannel.INTERLEAVED

    def _load_if_not(self):
        if self._img_data or self._handle is None:
            return
        p_options = lib.heif_decoding_options_alloc()
        p_options = ffi.gc(p_options, lib.heif_decoding_options_free)
        p_options.convert_hdr_to_8bit = int(self._heif_ctx.to_8bit)
        p_img = ffi.new("struct heif_image **")
        check_libheif_error(lib.heif_decode_image(self._handle, p_img, self._color(), self._chroma(), p_options))
        heif_img = ffi.gc(p_img[0], lib.heif_image_release)
        self._img_to_img_data_dict(heif_img)

    def _img_to_img_data_dict(self, heif_img):
        p_stride = ffi.new("int *")
        p_data = lib.heif_image_get_plane(heif_img, self._channel(), p_stride)
        stride = p_stride[0]
        data_length = self.size[1] * stride
        data_buffer = ffi.buffer(p_data, data_length)
        self._img_data.update(img=heif_img, data=data_buffer, stride=stride)

    def _create_image(self, src_data, src_stride: int, new_mode=None):
        width, height = self.size
        p_new_img = ffi.new("struct heif_image **")
        chroma = MODE_INFO[new_mode][3] if new_mode else self._chroma()
        error = lib.heif_image_create(width, height, self._color(), chroma, p_new_img)
        check_libheif_error(error)
        new_img = ffi.gc(p_new_img[0], lib.heif_image_release)
        depth = MODE_INFO[new_mode][1] if new_mode else self.bit_depth
        error = lib.heif_image_add_plane(new_img, self._channel(), width, height, depth)
        check_libheif_error(error)
        p_dest_stride = ffi.new("int *")
        dest_data = lib.heif_image_get_plane(new_img, self._channel(), p_dest_stride)
        dest_stride = p_dest_stride[0]
        src_data = ffi.from_buffer(src_data)
        if new_mode and new_mode != self.mode:
            MODE_CONVERT[self.mode][new_mode](src_data, src_stride, dest_data, dest_stride, height)
            self.mode = new_mode
        else:
            lib.copy_image_data(src_data, src_stride, dest_data, dest_stride, height)
        return new_img

    def _get_pure_data(self):
        new_stride = get_pure_stride(self.mode, self.size[0])
        new_size = new_stride * self.size[1]
        new_data = FFI_DRY_ALLOC("char[]", new_size)
        lib.copy_image_data(ffi.from_buffer(self.data), self.stride, new_data, new_stride, self.size[1])
        return ffi.buffer(new_data, new_size)


class HeifThumbnail(HeifImageBase):
    """Class represents a single thumbnail for a HeifImage."""

    def __init__(self, original_img, reference, thumb_id: int = None):
        if isinstance(original_img, HeifImage):
            p_handle = ffi.new("struct heif_image_handle **")
            check_libheif_error(lib.heif_image_handle_get_thumbnail(original_img._handle, thumb_id, p_handle))
            super().__init__(original_img._heif_ctx, p_handle[0])
        else:
            super().__init__(original_img, None)
        self.parent = ref(reference)

    def __repr__(self):
        _bytes = f"{len(self.data)} bytes" if self._img_data else "no"
        return (
            f"<{self.__class__.__name__} {self.size[0]}x{self.size[1]} {self.mode} "
            f"with {_bytes} image data> Original:{self.parent()}"
        )

    def __deepcopy__(self, memo):
        return self.clone()

    def clone(self, ref_original=None):
        heif_ctx = HeifCtxAsDict(self.mode, self.size, self.data, stride=self.stride)
        return HeifThumbnail(heif_ctx, ref_original if ref_original else heif_ctx)

    def get_original(self):
        """Return an :py:class:`~pillow_heif.HeifImage` frame to which thumbnail belongs.

        .. note:: It is useful when you traverse thumbnails with :py:meth:`~pillow_heif.HeifFile.thumbnails_all`

        :returns: :py:class:`~pillow_heif.HeifImage` or None."""

        referenced = self.parent()
        return referenced if isinstance(referenced, HeifImage) else None

    def clone_no_data(self):
        """Private. For use only when encoding an image."""

        heif_ctx = HeifCtxAsDict(self.mode, self.size, None, stride=0)
        return HeifThumbnail(heif_ctx, heif_ctx)


class HeifImage(HeifImageBase):
    """Class represents one frame in a :py:class:`~pillow_heif.HeifFile`"""

    def __init__(self, heif_ctx: Union[LibHeifCtx, HeifCtxAsDict], img_id=-1, primary=False, for_encoding=False):
        additional_info = {}
        if isinstance(heif_ctx, LibHeifCtx):
            p_handle = ffi.new("struct heif_image_handle **")
            if primary:
                error = lib.heif_context_get_primary_image_handle(heif_ctx.ctx, p_handle)
            else:
                error = lib.heif_context_get_image_handle(heif_ctx.ctx, img_id, p_handle)
            check_libheif_error(error)
            handle = p_handle[0]
            _metadata = read_metadata(handle)
            _exif = retrieve_exif(_metadata)
            _xmp = retrieve_xmp(_metadata)
            additional_info["metadata"] = _metadata
            _color_profile = read_color_profile(handle)
            if _color_profile:
                if _color_profile["type"] in ("rICC", "prof"):
                    additional_info["icc_profile"] = _color_profile["data"]
                    additional_info["icc_profile_type"] = _color_profile["type"]
                else:
                    additional_info["nclx_profile"] = _color_profile["data"]
        else:
            handle = None
            _exif = None
            _xmp = None
            additional_info["metadata"] = []
            additional_info.update(heif_ctx.additional_info)
        super().__init__(heif_ctx, handle, for_encoding)
        self.info = {
            "exif": _exif,
            "xmp": _xmp,
            "primary": primary,
        }
        self.info.update(**additional_info)
        self.thumbnails = self.__read_thumbnails()

    def __repr__(self):
        _bytes = f"{len(self.data)} bytes" if self._img_data else "no"
        return (
            f"<{self.__class__.__name__} {self.size[0]}x{self.size[1]} {self.mode} "
            f"with {_bytes} image data and {len(self.thumbnails)} thumbnails>"
        )

    def load(self):
        super().load()
        for thumbnail in self.thumbnails:
            thumbnail.load()
        return self

    def unload(self):
        super().unload()
        for thumbnail in self.thumbnails:
            thumbnail.unload()
        return self

    def scale(self, width: int, height: int):
        """Rescale image by a specific width and height given in parameters.

        .. note:: Image will be scaled in place. Images converted to some specific modes not always can be scaled.

        :param width: new image width.
        :param height: new image height."""

        self._load_if_not()
        p_scaled_img = ffi.new("struct heif_image **")
        check_libheif_error(lib.heif_image_scale_image(self.heif_img, p_scaled_img, width, height, ffi.NULL))
        scaled_heif_img = ffi.gc(p_scaled_img[0], lib.heif_image_release)
        self.size = (
            lib.heif_image_get_primary_width(scaled_heif_img),
            lib.heif_image_get_primary_height(scaled_heif_img),
        )
        self._img_to_img_data_dict(scaled_heif_img)
        return self

    def add_thumbnails(self, boxes: Union[List[int], int]) -> None:
        """Add thumbnail(s) to an image.

        .. note:: Method creates thumbnails without image data, they will be encoded during `save` operation.

        :param boxes: int or list of ints determining size of thumbnail(s) to generate for image.

        :returns: None"""

        if isinstance(boxes, list):
            boxes_list = boxes
        else:
            boxes_list = [boxes]
        self.load()
        for box in boxes_list:
            if box <= 3:
                continue
            if self.size[0] <= box and self.size[1] <= box:
                continue
            if self.size[0] > self.size[1]:
                thumb_height = int(self.size[1] * box / self.size[0])
                thumb_width = box
            else:
                thumb_width = int(self.size[0] * box / self.size[1])
                thumb_height = box
            thumb_height = thumb_height - 1 if (thumb_height & 1) else thumb_height
            thumb_width = thumb_width - 1 if (thumb_width & 1) else thumb_width
            if max((thumb_height, thumb_width)) in [max(i.size) for i in self.thumbnails]:
                continue
            __heif_ctx = HeifCtxAsDict(self.mode, (thumb_width, thumb_height), None, stride=0)
            self.thumbnails.append(HeifThumbnail(__heif_ctx, self))

    def copy_thumbnails(self, thumbnails: List[HeifThumbnail], **kwargs):
        """Private. For use only in ``add_from_pillow`` and ``add_from_heif``."""

        for thumb in thumbnails:
            if kwargs.get("for_encoding", False):
                cloned_thumb = thumb.clone_no_data()
            else:
                cloned_thumb = thumb.clone(ref_original=self)
            self.thumbnails.append(cloned_thumb)

    def __read_thumbnails(self) -> List[HeifThumbnail]:
        result: List[HeifThumbnail] = []
        if self._handle is None or not options().thumbnails:
            return result
        thumbs_count = lib.heif_image_handle_get_number_of_thumbnails(self._handle)
        if thumbs_count == 0:
            return result
        thumbnails_ids = ffi.new("heif_item_id[]", thumbs_count)
        thumb_count = lib.heif_image_handle_get_list_of_thumbnail_IDs(self._handle, thumbnails_ids, thumbs_count)
        for i in range(thumb_count):
            result.append(HeifThumbnail(self, self, thumb_id=thumbnails_ids[i]))
        return result


class HeifFile:
    """This class represents the :py:class:`~pillow_heif.HeifImage` classes container.

    To create :py:class:`~pillow_heif.HeifFile` object, use the appropriate factory functions.

    * :py:func:`~pillow_heif.open_heif`
    * :py:func:`~pillow_heif.from_pillow`
    * :py:func:`~pillow_heif.from_bytes`

    .. note:: To get empty container to fill it later, create a class without parameters."""

    def __init__(
        self, heif_ctx: Union[LibHeifCtx, HeifCtxAsDict] = None, img_ids: List[int] = None, main_id: int = None
    ):
        if heif_ctx is None:
            heif_ctx = HeifCtxAsDict("", (0, 0), None)
        self.images: List[HeifImage] = []
        self.mimetype = heif_ctx.get_mimetype() if isinstance(heif_ctx, LibHeifCtx) else ""
        if img_ids:
            for img_id in img_ids:
                self.images.append(HeifImage(heif_ctx, img_id, img_id == main_id))

    @property
    def original_bit_depth(self):
        """Points to :py:attr:`~pillow_heif.HeifImage.original_bit_depth` property of the
        primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self.images[self.primary_index()].original_bit_depth

    @property
    def bit_depth(self):
        """Points to :py:attr:`~pillow_heif.HeifImage.bit_depth` property of the
        primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self.images[self.primary_index()].bit_depth

    @property
    def size(self):
        """Points to :py:attr:`~pillow_heif.HeifImage.size` property of the
        primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self.images[self.primary_index()].size

    @property
    def mode(self):
        """Points to :py:attr:`~pillow_heif.HeifImage.mode` property of the
        primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self.images[self.primary_index()].mode

    @property
    def data(self):
        """Points to :py:attr:`~pillow_heif.HeifImage.data` property of the
        primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self.images[self.primary_index()].data

    @property
    def stride(self):
        """Points to :py:attr:`~pillow_heif.HeifImage.stride` property of the
        primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self.images[self.primary_index()].stride

    @property
    def has_alpha(self):
        """Points to :py:attr:`~pillow_heif.HeifImage.has_alpha` property of the
        primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self.images[self.primary_index()].has_alpha

    @property
    def info(self):
        """Points to ``info`` dict of the primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self.images[self.primary_index()].info

    @property
    def thumbnails(self):
        """Points to ``thumbnails`` of the primary :py:class:`~pillow_heif.HeifImage` in the container.

        :exception IndexError: If there is no images."""

        return self.images[self.primary_index()].thumbnails

    def primary_index(self, image_list=None) -> int:
        """Returns index of the ``PrimaryImage`` in the container."""

        if image_list is None:
            image_list = self.images
        i = 0
        for index, _ in enumerate(image_list):
            if _.info["primary"]:
                i = index
        return i

    def thumbnails_all(self, one_for_image: bool = False) -> Iterator[HeifThumbnail]:
        """Enums all thumbnails in all images.

        :param one_for_image: If set to ``True`` will return maximum one thumbnail for one image.

        :returns: Iterator for :py:class:`~pillow_heif.HeifThumbnail` classes."""

        for i in self:
            for thumb in i.thumbnails:
                yield thumb
                if one_for_image:
                    break

    def load(self, everything: bool = False):
        if everything:
            for img in self:
                img.load()
        else:
            self.images[self.primary_index()].load()
        return self

    def scale(self, width: int, height: int) -> None:
        """Scale primary image in the container. See :py:meth:`~pillow_heif.HeifImage.scale`"""

        self.images[self.primary_index()].scale(width, height)

    def add_from_pillow(self, pil_image: Image.Image, load_one=False, ignore_primary=True, **kwargs):
        """Add image(s) to container.

        :param pil_image: ``PIL.Image`` class to get images from.
        :param load_one: should be only one frame loaded. Default=``False``
        :param ignore_primary: force ``PrimaryImage=False`` flag to all added images."""

        if load_one:
            self.__add_frame_from_pillow(pil_image, ignore_primary, **kwargs)
        else:
            for frame in ImageSequence.Iterator(pil_image):
                self.__add_frame_from_pillow(frame, ignore_primary, **kwargs)
        return self

    def __add_frame_from_pillow(self, frame: Image.Image, ignore_primary: bool, **kwargs) -> None:
        if frame.width <= 0 or frame.height <= 0:
            return
        additional_info = {}
        supported_info_keys = (
            "exif",
            "xmp",
            "metadata",
            "primary",
            "icc_profile",
            "icc_profile_type",
            "nclx_profile",
        )
        for k in supported_info_keys:
            if k in frame.info:
                additional_info[k] = frame.info[k]
        if ignore_primary:
            additional_info["primary"] = False
        if "xmp" not in additional_info and "XML:com.adobe.xmp" in frame.info:
            additional_info["xmp"] = frame.info["XML:com.adobe.xmp"]
        if "xmp" in additional_info and isinstance(additional_info["xmp"], str):
            additional_info["xmp"] = additional_info["xmp"].encode("utf-8")
        original_orientation = set_orientation(additional_info)
        if frame.mode == "P":
            mode = "RGBA" if frame.info.get("transparency") else "RGB"
            frame = frame.convert(mode=mode)
        elif frame.mode == "LA":  # libheif doesnt not support INTERLEAVED_MONOCHROME mode
            frame = frame.convert(mode="RGBA")
        elif frame.mode == "I":
            frame = frame.convert(mode="I;16L")
        elif frame.mode == "1":
            frame = frame.convert(mode="L")

        if original_orientation is not None and original_orientation != 1:
            frame = ImageOps.exif_transpose(frame)
        added_image = self.add_frombytes(
            frame.mode,
            frame.size,
            frame.tobytes(),
            add_info={**additional_info},
            for_encoding=kwargs.get("for_encoding", False),
        )
        added_image.copy_thumbnails(frame.info.get("thumbnails", []), **kwargs)

    def add_from_heif(self, heif_image, load_one=False, ignore_primary=True, **kwargs):
        """Add image(s) to container.

        :param heif_image: ``HeifFile`` or ``HeifImage`` class to get images from.
        :param load_one: should be only one frame loaded. Default=``False``
        :param ignore_primary: force ``PrimaryImage=False`` flag to all added images."""

        if isinstance(heif_image, HeifFile):
            heif_images = list(heif_image)
        else:
            heif_images = [heif_image]
        for image in heif_images:
            additional_info = image.info.copy()
            if ignore_primary:
                additional_info["primary"] = False
            added_image = self.add_frombytes(
                image.mode,
                image.size,
                image.data,
                stride=image.stride,
                add_info={**additional_info},
                for_encoding=kwargs.get("for_encoding", False),
            )
            added_image.copy_thumbnails(image.thumbnails, **kwargs)
            if load_one:
                break
        return self

    def add_thumbnails(self, boxes: Union[List[int], int]) -> None:
        """Add thumbnail(s) to all images.

        :param boxes: int or list of ints determining size of thumbnail(s) to generate for images.

        :returns: None."""

        for img in self.images:
            img.add_thumbnails(boxes)

    def save(self, fp, **kwargs) -> None:
        """Saves image under the given fp.

        Keyword options can be used to provide additional instructions to the writer.
        If a writer does not recognise an option, it is silently ignored.

        Supported options:
            ``save_all`` - boolean. Should all images from ``HeiFile`` be saved.
            (default = ``True``)

            ``append_images`` - do the same as in Pillow.
            Accept ``HeifFile``, ``HeifImage`` and ``PIL.Image``

            .. note:: Appended images always will have ``info["primary"]=False``

            ``quality`` - see :py:attr:`~pillow_heif._options.PyLibHeifOptions.quality`

            ``enc_params`` - tuple of name:value to pass to :ref:`x265 <hevc-encoder>` encoder.

            ``exif`` - override primary image's EXIF with specified. Accept ``None`` or ``bytes``.

            ``xmp`` - override primary image's XMP with specified. Accept ``None`` or ``bytes``.

            ``primary_index`` - ignore ``info["primary"]`` and set `PrimaryImage` by index.

        :param fp: A filename (string), pathlib.Path object or file object.

        :returns: None
        :raises: :py:exc:`~pillow_heif.HeifError` or :py:exc:`ValueError`"""

        if not options().hevc_enc:
            raise HeifError(code=HeifErrorCode.ENCODING_ERROR, subcode=5000, message="No encoder found.")
        images_to_save = self.__get_images_for_save(self.images, **kwargs)
        if not images_to_save:
            raise ValueError("Cannot write file with no images as HEIF.")
        primary_index = kwargs.get("primary_index", None)
        if primary_index is None:
            primary_index = 0
            for i, img in enumerate(images_to_save):
                if img.info["primary"]:
                    primary_index = i
        elif primary_index == -1 or primary_index >= len(images_to_save):
            primary_index = len(images_to_save) - 1
        heif_ctx_write = LibHeifCtxWrite()
        heif_ctx_write.set_encoder_parameters(kwargs.get("enc_params", []), kwargs.get("quality", options().quality))
        self._save(
            heif_ctx_write,
            images_to_save,
            primary_index,
            primary_exif=kwargs.get("exif", -1),
            primary_xmp=kwargs.get("xmp", -1),
        )
        heif_ctx_write.write(fp)

    def __repr__(self):
        return f"<{self.__class__.__name__} with {len(self)} images: {[str(i) for i in self]}>"

    def __len__(self):
        return len(self.images)

    def __iter__(self):
        for _ in self.images:
            yield _

    def __getitem__(self, index):
        if index < 0 or index >= len(self.images):
            raise IndexError(f"invalid image index: {index}")
        return self.images[index]

    def __delitem__(self, key):
        if key < 0 or key >= len(self.images):
            raise IndexError(f"invalid image index: {key}")
        del self.images[key]

    def add_frombytes(self, mode: str, size: tuple, data, **kwargs):
        """Adds image from bytes to container.

        .. note:: Supports ``stride`` value if needed.

        :param mode: `BGR(A);16`, `L;16`, `I;16L`, `RGB(A);12`, `L;12`, `RGB(A);10`, `L;10`, `RGB(A)`, `BGR(A)`, `L`
        :param size: tuple with ``width`` and ``height`` of image.
        :param data: bytes object with raw image data.

        :returns: :py:class:`~pillow_heif.HeifImage` object that was appended to HeifFile."""

        for_encoding = kwargs.get("for_encoding", False)
        added_image = HeifImage(HeifCtxAsDict(mode, size, data, **kwargs), for_encoding=for_encoding)
        self.images.append(added_image)
        return added_image

    @staticmethod
    def _save(ctx: LibHeifCtxWrite, img_list: List[HeifImage], primary_index: int, **kwargs) -> None:
        enc_options = lib.heif_encoding_options_alloc()
        enc_options = ffi.gc(enc_options, lib.heif_encoding_options_free)
        for i, img in enumerate(img_list):
            set_color_profile(img.heif_img, img.info)
            p_img_handle = ffi.new("struct heif_image_handle **")
            error = lib.heif_context_encode_image(ctx.ctx, img.heif_img, ctx.encoder, enc_options, p_img_handle)
            check_libheif_error(error)
            new_img_handle = ffi.gc(p_img_handle[0], lib.heif_image_handle_release)
            exif = img.info["exif"]
            xmp = img.info["xmp"]
            if i == primary_index:
                if i:
                    lib.heif_context_set_primary_image(ctx.ctx, new_img_handle)
                if kwargs["primary_exif"] != -1:
                    exif = kwargs["primary_exif"]
                if kwargs["primary_xmp"] != -1:
                    xmp = kwargs["primary_xmp"]
            set_exif(ctx, new_img_handle, exif)
            set_xmp(ctx, new_img_handle, xmp)
            set_metadata(ctx, new_img_handle, img.info)
            for thumbnail in img.thumbnails:
                thumb_box = max(thumbnail.size)
                if max(img.size) > thumb_box > 3:
                    p_new_thumb_handle = ffi.new("struct heif_image_handle **")
                    error = lib.heif_context_encode_thumbnail(
                        ctx.ctx,
                        img.heif_img,
                        new_img_handle,
                        ctx.encoder,
                        enc_options,
                        thumb_box,
                        p_new_thumb_handle,
                    )
                    check_libheif_error(error)
                    if p_new_thumb_handle[0] != ffi.NULL:
                        lib.heif_image_handle_release(p_new_thumb_handle[0])

    @staticmethod
    def __get_images_for_save(images: List[HeifImage], **kwargs) -> List[HeifImage]:
        """Accepts list of Union[HeifFile, HeifImage, Image.Image] and returns List[HeifImage]"""

        images_to_save = images + list(kwargs.get("append_images", []))
        save_one = not kwargs.get("save_all", True)
        if save_one:
            images_to_save = images_to_save[:1]
        result = []
        for img in images_to_save:
            no_primary = not bool(img in images)
            if isinstance(img, Image.Image):
                heif_file = HeifFile().add_from_pillow(img, save_one, no_primary, for_encoding=True)
            else:
                heif_file = HeifFile().add_from_heif(img, save_one, no_primary, for_encoding=True)
            result += list(heif_file)
        return result


def check_heif(fp):
    """Wrapper around `libheif.heif_check_filetype` function.

    .. note:: If `fp` contains less 12 bytes, then always return `HeifFiletype.NO`

    :param fp: See parameter ``fp`` in :func:`is_supported`

    :returns: Value from :py:class:`~pillow_heif.HeifFiletype` enumeration."""

    magic = _get_bytes(fp, 16)
    return HeifFiletype.NO if len(magic) < 12 else lib.heif_check_filetype(magic, len(magic))


def is_supported(fp) -> bool:
    """Checks if the given `fp` object contains a supported file type,
    by calling :py:func:`~pillow_heif.check_heif` function.

    Look at :py:attr:`~pillow_heif._options.PyLibHeifOptions.strict` property for additional info.

    :param fp: A filename (string), pathlib.Path object or a file object.
        The file object must implement ``file.read``,
        ``file.seek``, and ``file.tell`` methods,
        and be opened in binary mode.

    :returns: A boolean indicating if object can be opened."""

    magic = _get_bytes(fp, 16)
    heif_filetype = check_heif(magic)
    if heif_filetype == HeifFiletype.NO or (not options().avif and magic[8:12] in (b"avif", b"avis")):
        return False
    if heif_filetype in (HeifFiletype.YES_SUPPORTED, HeifFiletype.MAYBE):
        return True
    return not options().strict


def open_heif(fp, convert_hdr_to_8bit=True) -> HeifFile:
    """Opens the given HEIF image file.

    :param fp: See parameter ``fp`` in :func:`is_supported`
    :param convert_hdr_to_8bit: Boolean indicating should 10 bit or 12 bit images
        be converted to 8 bit images during loading.

    :returns: An :py:class:`~pillow_heif.HeifFile` object.
    :exception HeifError: If file is corrupted or is not in Heif format."""

    heif_ctx = LibHeifCtx(fp, convert_hdr_to_8bit)
    return HeifFile(heif_ctx, heif_ctx.get_top_images_ids(), heif_ctx.get_main_img_id())


def read_heif(fp, convert_hdr_to_8bit=True) -> HeifFile:
    """Opens the given HEIF image file and decodes all images.

    .. note:: In most cases it better to call :py:meth:`~pillow_heif.open_heif`, and
        let images decoded automatically only when needed.

    :param fp: See parameter ``fp`` in :func:`is_supported`
    :param convert_hdr_to_8bit: Boolean indicating should 10 bit or 12 bit images
        be converted to 8 bit images during loading.

    :returns: An :py:class:`~pillow_heif.HeifFile` object.
    :exception HeifError: If file is corrupted or is not in Heif format."""

    heif_file = open_heif(fp, convert_hdr_to_8bit)
    heif_file.load(everything=True)
    return heif_file


def from_pillow(pil_image: Image.Image, load_one: bool = False, ignore_primary=True) -> HeifFile:
    """Creates :py:class:`~pillow_heif.HeifFile` from a Pillow Image.

    :param pil_image: Pillow :external:py:class:`~PIL.Image.Image` class.
    :param load_one: If ``True``, then all frames will be loaded.
    :param ignore_primary: force ``PrimaryImage=False`` flag to all added images.

    :returns: An :py:class:`~pillow_heif.HeifFile` object."""

    return HeifFile().add_from_pillow(pil_image, load_one, ignore_primary)


def from_bytes(mode: str, size: tuple, data, **kwargs) -> HeifFile:
    """Creates :py:class:`~pillow_heif.HeifFile` from bytes.

    .. note:: Supports ``stride`` value if needed.

    :param mode: `BGR(A);16`, `L;16`, `I;16L`, `RGB(A);12`, `L;12`, `RGB(A);10`, `L;10`, `RGB(A)`, `BGR(A)`, `L`
    :param size: tuple with ``width`` and ``height`` of image.
    :param data: bytes object with raw image data.

    :returns: An :py:class:`~pillow_heif.HeifFile` object."""

    _ = HeifFile()
    _.add_frombytes(mode, size, data, **kwargs)
    return _


# --------------------------------------------------------------------
# DEPRECATED FUNCTIONS.
# pylint: disable=unused-argument
# pylint: disable=redefined-builtin


def check(fp):
    warn("Function `check` is deprecated, use `check_heif` instead.", DeprecationWarning)
    return check_heif(fp)  # pragma: no cover


def open(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):  # noqa
    warn("Function `open` is deprecated and will be removed, use `open_heif` instead.", DeprecationWarning)
    return open_heif(fp, convert_hdr_to_8bit=convert_hdr_to_8bit)  # pragma: no cover


def read(fp, *, apply_transformations=True, convert_hdr_to_8bit=True):  # noqa
    warn("Function `read` is deprecated and will be removed, use `open_heif` instead.", DeprecationWarning)
    return open_heif(fp, convert_hdr_to_8bit=convert_hdr_to_8bit)  # pragma: no cover
