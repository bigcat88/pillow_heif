All notable changes to this project will be documented in this file.

## [1.1.1 - 2025-09-30]

### Fixed

- macOS: Wheels now support older macOS versions like Catalina (x86_64 CPU) or Ventura (ARM CPU). #384 #385

## [1.1.0 - 2025-08-02]

### Added

- Python `3.14` wheels added.

### Changed

- `libheif` was updated from the `1.19.8` to `1.20.1` version.

### Fixed

- `x265` was updated to the `4.1` version for Linux build to be in sync with macOS and Windows.

## [1.0.0 - 2025-06-29]

### Added

- Support for `YCbCr` AUX images. #355  Thanks to @marklit for feature request and test file.

### Changed

- `AVIF` support was dropped, as the new upcoming Pillow has native `AVIF` support. #345
- `libheif` was updated from the `1.19.7` to `1.19.8` version. #349
- `libde265` was updated from the `1.0.15` to `1.0.16` version.
- Removed deprecated PyPy 3.9 wheels & added PyPy 3.11 wheels.

## [0.22.0 - 2025-03-15]

### Added

- Boolean `pillow_heif.options.DISABLE_SECURITY_LIMITS` to bypass security limit of libheif for the image size. #328

### Changed

- `libx265` library was updated to the latest `4.1` version.
- `libheif` was updated from the `1.19.5` to `1.19.7` version.
- `AVIF` format marked as deprecated and pending for the removal.

## [0.21.0 - 2024-11-29]

### Added

- Allow specifying encoder parameters for non-primary images in image sequence. #313

### Changed

- Libheif updated from `1.18.2` to `1.19.5` version. #312
- For macOS(`x86_64`), the minimum supported version for binary wheels has been raised from `12` to `13`.

### Fixed

- Error `argument '-Ofast' is deprecated` when building from source. #305

## [0.20.0 - 2024-10-19]

### Added

- Initial support for parsing auxiliary images. #297 Thanks to @johncf

### Changed

- Libheif updated from `1.18.1` to `1.18.2` version. #278
- Dropped `Python 3.8` support. #293

### Fixed

- More accurate error handling in the `C` module. #298 Thanks to @johncf
- Support for `Pillow` **11.0.0** #294

## [0.18.0 - 2024-07-27]

### Added

- `image.info["heif"]` dictionary with `camera_intrinsic_matrix` HEIF specific metadata. Currently only reading is supported. #271

### Changed

- libheif updated from `1.17.6` to `1.18.1` version.  #249
- Python `3.13.0b3` wheels added; macOS **arm64** Python3.8 wheels dropped. #272

## [0.17.0 - 2024-07-02]

### Added

- Support for `Pillow` **10.4.0** #254

### Changed

- Minimum supported Pillow version raised to `10.1.0`. #251
- `xmp` in `info` dictionary is now not present if it is empty. #254

### Fixed

- Processing of the images in `P` mode with `transparency` = 0. #238

## [0.16.0 - 2024-04-02]

This release contains breaking change for monochrome images.

### Added

- Monochrome images **without alpha** channel, will be opened in `L` or `I;16` mode instead of `RGB`. #215

### Changed

- `convert_hdr_to_8bit` value now ignores `monochrome` images. #215
- `subsampling` parameter for encoding has higher priority than `chroma`. #213
- Minimum required `libehif` version is `1.17.0`. #214
- Minimum supported Pillow version raised to `9.5.0`. #216

## [0.15.0 - 2024-02-03]

### Added

- `libheif_info` function: added `encoders` and `decoders` keys to the result, for future libheif plugins support. #189
- `options.PREFERRED_ENCODER` - to use `encoder` different from the default one. #192
- `options.PREFERRED_DECODER` - to use `decoder` different from the default one. #193

### Changed

- libde265 updated from `1.0.14` to `1.0.15`. [changelog](https://github.com/strukturag/libde265/releases/tag/v1.0.15)
- libheif updated from `1.17.5` to `1.17.6`. [changelog](https://github.com/strukturag/libheif/releases/tag/v1.17.6)

## [0.14.0 - 2023-12-02]

### Added

- Synonym for `chroma` encoder parameter: `subsampling`(usage is the same as in Pillow JPEG). #161 #165
- Passing `image_orientation` value to libheif, instead of manually rotating image according to EXIF before encoding. #168
- Pillow plugin: support for images in `YCbCr` mode for saving without converting to `RGB`. #169
- Pi-Heif: Python3.12 32-bit `armv7` wheels. #160

### Changed

- Increased the minimum required libheif version to `1.14.1`.
- Linux: When building from source, `libheif` and other libraries are no longer try built automatically. #158
- Libheif updated from `1.16.2` to `1.17.5` version. #166 #175
- `NCLX` color profile - was reworked, updated docs, see PR for more info. #171
- Minimum supported Pillow version raised to `9.2.0`.
- Pi-Heif: As last libheif version requires minimum `cmake>=3.16.3` dropped Debian `10 armv7` wheels. #160
- libde265 updated from `1.0.12` to `1.0.14`. [changelog](https://github.com/strukturag/libde265/releases/tag/v1.0.13)

### Fixed

- Support of libheif `1.17.x`. #156
- Windows : Build from source with MinGW Python. #178

## [0.13.1 - 2023-10-15]

### Added

- Returned `PyPy 3.8` wheels.

### Changed

- Linux: `libaom` updated to `3.6.1`, `musllinux` builds switched to `musllinux_1_2` tag.

### Fixed

- When building from source, the installer additionally searches for `libheif` using `pkg-config`. #128

## [0.13.0 - 2023-08-09]

### Added

- `Python 3.12`, `PyPy 3.10` wheels.
- `Depth Image` read support, they are available as a list in `im.info["depth_images"]` #116
- `options.SAVE_NCLX_PROFILE` - default `False` to be full compatible with previous versions, but in next versions may be changed to `True`. #118 Thanks to @wiggin15
- Support for `Pillow 10.1.0`

### Changed

- The license for the project itself has been changed to "BSD-3-Clause" since "Apache 2.0" is not compatible with the "x265" encoder. #111 Thanks to @mattip
- Minimum required `Pillow` version increased from `8.4.0` to `9.1.1`
- Dropped `Python 3.7` support, `PyPy 3.8` wheels.
- Dropped 32-bit wheels for `Pillow-Heif`. `Pi-Heif` still have 32-bit wheels.

## [0.12.0 - 2023-07-08]

This release is fully compatible with previous versions.

### Added

- (Heif) restored lost ability after `0.9.x` versions to open HDR images in 10/12 bit. #96

### Changed

- `libde265`(HEIF decoder) updated from 1.0.11 to 1.0.12 version. [changelog](https://github.com/strukturag/libde265/releases/tag/v1.0.12)
- `libheif` updated to `1.16.2`.

### Fixed

- Building from source when using `apt-repository ppa:strukturag/libheif`
- (Heif) `encode` function with `stride` argument correctly saves image.
- (Heif) HeifFile class created with `from_bytes` function with `stride` argument respect `stride` value during save.
- (Heif) HeifFile class created with `from_bytes` function with `stride` argument can correctly translate to the numpy array.

## [0.11.1 - 2023-05-10]

This release is fully compatible with `0.10.x` versions.

### Fixed

- Revert EXIF changes from `0.11.0` - raw data again can begin with `Exif\x00\x00`. Thanks to @fabbaum #93
- (Heif) `deepcopy` support for HeifFile class.

## [0.11.0 - 2023-04-30]

### Changed

- EXIF raw data in info["exif"] is now skipping first 6 bytes(`Exif\x00\x00`). Like in Pillow for WEBP.

### Fixed

- EXIF parsing(Xiaomi images and possible others). Thanks to @mxsleo #92
- (Pillow) `deepcopy` support for HeifImageFile and AvifImageFile
- (macOS, arm64) `libde265`(HEIF decoder) now has the same version as in other builds(`1.0.8`->`1.0.11`)
- (macOS, arm64) `libaom`(AVIF) now has the same version as in other builds(`3.4.0`->`3.6.0`)

## [0.10.1 - 2023-04-03]

### Added

- Windows PyPy wheels.
- Faster image loading implementation with Pillow `9.5.0`
- `options.ALLOW_INCORRECT_HEADERS` option to allow loading files with invalid `ispe` header. Thanks to @Soooda #86

### Changed

- `libheif` updated from `1.14.2` to `1.15.2`

## [0.10.0 - 2023-02-24]

Reworked version with the native C extension.

### Added

- Restored ability to build from source with libheif==1.12.0
- Ability to encode images in `LA` mode

### Changed

- `libde265`(HEIF decoder) updated from 1.0.9 to 1.0.11 version. [changelog](https://github.com/strukturag/libde265/releases/tag/v1.0.10)
- (Heif) `convert_to` method was removed, `bgr_mode` opt. parameter added to `open_heif`
- Many other changes, mostly for standalone usage. [topic](https://github.com/bigcat88/pillow_heif/issues/75)

### Changed

- Fixed Access Violation(all versions were affected) when image size after decoding differs. #79

## [0.9.3 - 2023-01-22]

### Fixed

Two bugs in XMP metadata handling that were causing exceptions. All versions were affected.
Thanks to @eeyrw for pointing out such a problem.

- Handling XMP data with `zero` byte at the end. #69
- Handling XMP data in `latin1` encoding. #69

## [0.9.2 - 2023-01-18]

### Changed

- libheif updated from `1.14.0` to `1.14.2`

## [0.9.1 - 2023-01-02]

### Changed

- info["nclx_profile"] changed the type from bytes(format of which was not described) to dict.
- Drop support for Python 3.6, PyPy 3.7. Added PyPy 3.9 wheels.
- `convert_to` method: `RGBa` to `RGB` mode support was removed(last Pillow supports it). #67

### Fixed

- Small memory leak when opening image with `nclx` color profile. #64

## [0.9.0 - 2022-12-15]

### Changed

- Minimum supported version of `libheif` to build from source is `1.13.0`
- Minimum required `Pillow` version increased from `6.2.0` to `8.3.0`, `getxmp` is used from Pillow now. #55
- `options()` was reworked. Added new `DECODE_THREADS` option. #57

### Fixed

- Added ability to `save` method to accept `exif` as `PIL.Image.Exif` class. #51
- Linux, Windows: fixed disabled multithreading for image decode. Added tests for this. Thanks to @jtressle #53
- Linux: building from source has been reworked to no longer require `autoconf`, `automake` and `pkg-config`.

## [0.8.0 - 2022-11-20]

### Added

- Armv7: wheels for Alpine 3.14+ with `musllinux_1_2_armv7l` tag.

### Changed

- `libheif` updated  to `1.14.0` version
- Ability to pass `enc_params` for save as `List[Tuple[str, str]]` was removed, now it accepts only `Dict`.
- Deprecated `options().ctx_in_memory` was removed(default behaviour does not change).
- Deprecated `options().strict` was removed(default behaviour does not change).
- Deprecated `check`, `open`, `read`, `check_heif` functions was removed.
- `scale` method marked as deprecated. Will be removed in `0.9.0` version.

### Fixed

- Values in `enc_params` for `save` can now be of type `int` or `float` and will be automatically converted to `str`.
- Armv7: wheels supports Debian 10(was only Debian 11+\Ubuntu 20.04+ previously) with `manylinux_2_28_armv7l` tag.
- Armv7: wheels sizes decreased significantly(almost in `3x`).

## [0.7.2 - 2022-10-31]

### Fixed

- (HeifImagePlugin) register proper `mimetype` for `HEIF` format. #47
- (HeifImagePlugin) decode image even when `EXIF` data is corrupted. #48
- (HeifImagePlugin) correct processing of `EXIF` that do not start with `b'EXIF'` (Pillow `9.3.0`). #46

## [0.7.1 - 2022-10-28]

### Added

- Support for images with a `premultiplied alpha` channel (Pillow does not fully support these).
- (Heif) `premultiplied_alpha` read-write property.
- (Heif) `to_pillow` method to `HeifFile` class.
- (Heif) `RGBA;16` -> `RGBA` conversion.
- (Heif) `RGBa` -> `RGB` conversion.

### Changed

- `libaom` updated from `3.4.0` to `3.5.0` version. [changelog](https://aomedia.googlesource.com/aom/+/refs/tags/v3.5.0)
- `libde265` updated from `1.0.8` to `1.0.9`.
- (Heif) The `get_file_mimetype` function has been reworked and is now written in python.
- (Heif) The `is_supported` function has been reworked and is now written in python.
- `options().strict` option marked as deprecated and will be removed in `0.8.0`.
- (Heif) `check_heif`function marked as deprecated.

### Fixed

- (Heif) `convert_to` should do nothing if the target `mode` is already the current image mode.
- (AvifImagePlugin) do not register or accept `.avifs` files, libheif does not support them.
- Images in `CMYK` mode will be converted for `RGBA` mode during saving instead of throwing `KeyError` exception.

## [0.7.0 - 2022-09-11]

This release is fully compatible with previous versions.

### Changed

- `libheif` updated to version `1.13.0`
- License for project itself changed to `Apache 2.0`

## [0.6.1 - 2022-08-21]

This release contains security and bug fixes.

### Changed

- Speed boost for AVIF encoding(+50%). [commit](https://github.com/strukturag/libheif/commit/4ec2ac35e2cd79e8594092f6e36b5eace19cefdf)

### Fixed

- (Linux, Windows) libde265: CVE-2022-1253, CVE-2021-36408, CVE-2021-36410, CVE-2021-35452, CVE-2021-36411 [MSYS2 PR](https://github.com/msys2/MINGW-packages/pull/12513)
- libheif: with chroma=`420`(which is a default mode) encoded images are closer to the originals with arrived patches. [libheif issue](https://github.com/strukturag/libheif/issues/521)
- libheif: scaling of images in some cases:  [commit](https://github.com/strukturag/libheif/commit/0cd461e18b99d018f9adef731eec928781078afb)
- Total `21` patches with fixes from official libheif repo has arrived.

## [0.6.0 - 2022-08-06]

This release is fully compatible with previous versions if was not using `AVIF` decoding before.

### Added

- (Heif) `save` method accepts optional parameter `format`. If `format="AVIF"` output file will be encoded in `h264` format using `AOM`.
- `AvifImagePlugin` introduced. Usage: `register_avif_opener()` or `import pillow_heif.AvifImagePlugin`
- After registering `AvifImagePlugin` you can work with `.avif` files the same way you do with `.heic`

### Changed

- (HeifImagePlugin) By default not accepts `.avif` files, register `AvifImagePlugin` if you need that. If you use `pillow_avif` then do not =)
- `options().hevc_enc` property was removed.
- `options().avif` property was removed.

### Fixed

- Better compatibility with `pillow_avif` package.
- (Linux) Wheels size decreased significantly(almost in `2x`).
- (Linux) Building from source is a bit simpler, you can build it with your custom libraries from now.
- (Linux) Great speed boost for encoding with new build type(it is as fast now as in Windows builds).

## [0.5.1 - 2022-07-30]

This release is fully compatible with `0.5.0` version.

### Added

- `chroma=4xx` optional subsampling parameter for `save`. Equivalent to `enc_params=[("chroma", "4xx")]` in old versions.

### Changed

- `enc_params` for `save` changed type from `List[Tuple[str, str]]` to `Dict`. Old code will still work, but marked as deprecated.
- `libheif_info` now returns also bundled versions of `x265` and `aom`.
- `options().avif` marked as deprecated. Starting from `0.6.0` version to register an `AVIF` plugin there will be a separate function, and it will be disabled by default.
- `options().hevc_enc` marked as deprecated and will be removed in `0.6.0`.

### Fixed

- Rare situation when exif orientation is `1` and xmp orientation different from `1` present at same time.
- XMP tags orientation that is generated by `exiftool` in some cases.
- Updated `libaom` on Linux and Windows from `3.3.0` to `3.4.0` version. MacOS builds had already that version in `0.5.0`.
- Pillow plugin now does not register `save` methods for `HEIF` format if build does not contain `HEIF` encoder(for custom build from source).
- Slight speed optimizations for working in a `Pillow` plugin mode.

## [0.5.0 - 2022-07-21]

Thumbnails were reworked, if was not use them before, then this release is fully compatible with `0.4.0` version.
It is a final API release, no more further changes to existing API are planned, only bugfixes, etc.

### Added

- (Heif, HeifImagePlugin) `thumbnail` function, `docs` for it.
- `__numpy_array__` property to `HeifFile`
- `convert_to` method to `HeifFile`

### Changed

- Wheels now are in ABI3 format for CPython(`cp3x-abi3-xxx.whl`), `3x` less size on PyPi.
- (Heif) `to_pillow` method, now fills `metadata` from an original image if was called for thumbnails.
- (HeifImagePlugin) During `open` `current frame` in multi frame images are set to index of `Primary Image`.
- (Heif) `add_thumbnails` method moved from `HeifFile`/`HeifImage` to separate file and now can accept a `PIL Image`.

### Fixed

- (HeifImagePlugin) Nice `speed up` for reading images having thumbnails in a `Pillow plugin` mode.
- (HeifImagePlugin) `XMP` metadata save from `TIFF` and `JPEG`.
- (HeifImagePlugin) `EXIF` metadata save from `TIFF`(only for Pillow >= 9.2).
- (HeifImagePlugin) Not to change the index of a current frame during saving multi-frame images.

## [0.4.0 - 2022-07-04]

### Added

- (Heif) - Numpy array interface support.
- (Heif) - `add_from_bytes` method  and `from_bytes` function added. Allows to read 16-bit color images with `OpenCV`(or any other library) and save it as 10(12) bit HEIF.
- (Heif) - `convert_to` method to `HeifImage` to provide an easy way to open 10 or 12 bit images as 16 bit for `OpenCV`(or any other library)
- (Heif, HeifImagePlugin) - support for saving images from `I`, `I;16`, `BGRA;16`, `BGR;16`, `BGRA`, `BGR` modes.
- (Heif) - added `save_to_12bit` to `options`, default `False`. Determines what bitness will have converted 16-bit images during saving.

### Changed

- **IMPORTANT!!!** `10/12` bit images changed their byte order from `Big Endian` to `Little Endian`. Probably no one still uses that API, but who knows...
- (Heif) - `HeifFile.chroma` and `HeifFile.color` properties was removed(they were not documented so probably no one will notice this), that info now stored in `mode`.
- (Heif, HeifImagePlugin) - `mode` for `10`/`12` bits was changed and accepts wider range of values, look [here](https://pillow-heif.readthedocs.io/en/latest/image-modes.html)
- Docs were `updated` & `rewritten` to reflect all those changes.

### Fixed

- `Examples` were `fixed` & `rewritten`(were broken from `0.3.1`+ versions).
- `exif` loading in HEIF sequence for `Pillow 9.2+` (https://github.com/python-pillow/Pillow/pull/6335)

## [0.3.2 - 2022-06-25]

### Fixed

- Support of saving images with mode=`"1"` in `"L"` mode.
- Images with mode=`"L"` are now saved natively in `Monochrome` mode(increase speed & decreased required memory and a bit less size)
- Speed optimization for `save` `append_images` parameter
- Possible `SEGFAULT` during encoding with some `stride` values.

## [0.3.1 - 2022-06-17]

### Added

- (Heif) - `HeifFile` gets `images: List[HeifImage]` and alternative method of changing order of images by editing it.
- (HeifImagePlugin) - `info` image dictionary can be now edited in place, and it will be saved for image sequences.

### Changed

- Updated docs.

### Fixed

- (HeifImagePlugin) Again fixing image order, for Pillow plugin it was not fixed fully in 0.3.0.
- Optimizing code.

## [0.3.0 - 2022-06-11]

### Added

- (HeifImagePlugin, Heif) - `save` now recognizes `exif=` and `xmp=` optional parameters. Works as in other Pillow plugins. #25
- (HeifImagePlugin, Heif) - `save` now recognizes `primary_index` optional parameter.
- (HeifImagePlugin, Heif) - `info["primary"]` value.
- (Heif) - `primary_index` method to `HeifFile` class.
- Docs: [Encoding](https://pillow-heif.readthedocs.io/en/latest/encoding.html)
- Docs: [Changes in Order Of Images](https://pillow-heif.readthedocs.io/en/latest/v0.3-order-of-images.html)

### Changed

- Changed image order when multiply images present, `HeifFile` points to primary image as it was before, but it **can be not** the first image in a list.
- When using as a Pillow's plugin the only way to know is an image `Primary` or not is to perform check of `info["primary"]` value.
- (Heif) - optimized code of `HeifImageThumbnail`, added `get_original` method.

### Fixed

- (HeifImagePlugin) - `save` bug, when first frame was saved instead of current.
- Minor usage fixes and optimizations.

## [0.2.5 - 2022-05-30]

### Added

- (HeifImagePlugin) - support for `PIL.ImageFile.LOAD_TRUNCATED_IMAGES` flag.
- (Windows, encoder) - encoding of `10` and `12` bit images. #24

### Changed

- (Windows) - replaced `vcpkg` build by `MSYS2`(MinGW) build, report of any possible bugs you see.

## [0.2.4 - 2022-05-18]

### Added

- (HeifImagePlugin) - saving of XMP tags from PNG.
- Benchmarks page to docs.

### Changed

- Added option `ctx_in_memory`, default=True. Benchmarks showed that versions `0.1.x` which worked like that, was much faster.
This will not affect any user code, changes are internal.

### Fixed

- (HeifImagePlugin) - XMP Orientation tag.
- (HeifImagePlugin, encoder) L and LA color modes. #23 (@Jarikf)

## [0.2.3 - 2022-05-02]

### Added

- Documentation has arrived.
- (HeifImagePlugin) - `custom_mimetype` field added like in other Pillow's plugins, instead of `info["brand"]`
- (Heif) - `mimetype` field added to `HeifFile` class, instead of `info["brand"]`

### Changed

- (Heif) - `apply_transformations` parameter in function `open_heif` was removed.
- (HeifImagePlugin, Heif) - removed `brand` and `main` values from `info` dictionary.
- (Heif) - added `original_bit_depth` property. It will not break any existing code. See docs.
- (Heif) - function `reset_orientation` was renamed to `set_orientation`.

### Fixed

- (HeifImagePlugin, Heif) - fix `exif` rotation, when converting from non `heif` to `heif`. See in docs chapter: `Workarounds`
- (HeifImagePlugin, Heif) - allow saving empty HeifFile when `append_images` parameter present.
- (HeifImagePlugin, Heif) - during saving, `fp` will be open after encoding process finished, and not before start.
- (Heif) - `HeifImage.chroma` and `HeifImage.color` property now available before the image load, right after `open`.

## [0.2.2 - 2022-04-23]

### Added

- PyPy 3.9 wheels.
- (HeifImagePlugin, Heif) `append_images` parameter to `save` methods.
- (HeifImagePlugin) - `import pillow_heif.HeifImagePlugin` for automatic Pillow plugin registration(as alternative to calling `register_heif_opener`).
- (HeifImagePlugin, Heif) `quality` can be now `-1` which indicates a lossless encoding.
- (HeifImagePlugin) - `getxmp` method. Works the same way as in Pillow's `PngImagePlugin` | `JpegImagePlugin`.
- (Heif) - added raw `xml` as `info["xml"]` and public function `pillow_heif.getxmp`(the same as for `HeifImagePlugin`)

### Fixed

- (HeifImagePlugin, Heif) - `Memory Leak` when `Opening` images, that appear in version 0.2.0 was `Slain Like a Hydra` (C)
- (HeifImagePlugin) - closing exclusive `fp`, this bug was only in 0.2.0+ versions.
- (HeifImagePlugin, Heif) - rare Python crash, with specific `strides` of thumbnails. More tests for that.
- (HeifImagePlugin, Heif) - Python crash when HeifFile closes its HeifImages when they are still referenced.

## [0.2.1 - 2022-04-17]

### Added

- (Windows) Build script by default assumes that `libheif ` installed in `C:\vcpkg\installed\x64-windows`, if `VCPKG_PREFIX` environment is missing.
- (Heif) `reader_add_thumbnail` and `reader_remove_image` examples.
- (Heif) `to_pillow` method and adjusted examples to use it.

### Changed

- (Heif) Removed `HeifSaveMask`, `get_img_thumb_mask_for_save` that was previously introduced, instead added `__delitem__` to `HeifFile`.
- Thumbnail encoding features reworked to simplify api. See `add_thumbnails` methods in `HeifFile` and `HeifImage` classes.

### Fixed

- (HeifImagePlugin) Fixed palette images with bytes transparency conversion. #21 (@Jarikf)
- (Heif) Raises `ValueError` when trying to save empty(no images) file.
- (HeifImagePlugin) Skips images with sizes = `0` during save, if there are no images, raise `ValueError`.
- (HeifImagePlugin) Memory optimizations, when there is only one image in file.
- Added licenses for libraries in binary wheels.
- (Windows) Fix docs for building and developing.
- (Heif) `add_from_pillow` method, now adds thumbnails from Pillow if it is `HeifImageFile(ImageFile.ImageFile)` class.

## [0.2.0 - 2022-04-09]

### Added

- encoding of images and thumbnails.
- `save` and `save_all` methods for Pillow plugin.
- `save` method for `HeifFile` class.
- `from_pillow` method, to init `HeifFile` class from Pillow.
- `add_heif` method for `HeifFile` class, to concatenate two heic files.
- more examples.

### Changed

- `read_heif` in process of deprecation. When you read `data` or `stride` properties image will be loaded automatically.
- `Undecoded*` classes was removed.
- Input files are now not read to memory, they will be read them from `fp` object only when need something.
  You can use old `load` and `close(fp_only=true)` to read it form `fp` and close it.
- thumbnails are enabled by default.
- many other minor changes.
- in future there will be fewer changes to api, this project goes to `stable` version from now.

### Fixed

- Speed and memory optimisations.

## [0.1.11 - 2022-03-24]

### Added

- Linux aarch64 PyPy 3.7 & 3.8 wheels.
- wrapper for libheif function `get_file_mimetype`.
- `burst`(container) image support(`ImageSequence`) for `heic` and `hif` when using as a pillow plugin.
- convert to jpg example for both `reader` and `plugin` use.
- in addition to iterator, to loop throw all images, `(Undecoded)``HeifFile` class now support access images by index.

### Changed

- `heif_brand_*` constants was removed, as mentioned in changes for 0.1.9 version.

### Fixed

- memory leak when working with thumbnails, now properly releases the thumbnail handle.
- rare bug with garbage collector for PyPy.
- `as_opener` register `image/heic` mimetype in addition to `image/heif`.
- `as_opener` also registers `.heif` extension, thanks @dust-to-dust for pointing that.
- `as_opener` sets `orientation` tag to `1` from `Exif` to not rotate image twice(`libheif` already do transforms)
- for `reader` you can do that manually if needed, with new `reset_orientation` function.

## [0.1.10 - 2022-03-17]

### Added

- macOS Intel PyPy3.7 & PyPy3.8 v7.3 wheels.
- class `HeifCompressionFormat(IntEnum)`. `have_decoder_for_format` and `have_encoder_for_format` functions.
- function `libheif_info` that returns dictionary with the version and available (en)(de)coders.
- class `HeifThumbnail` for thumbnails, see in examples. Only for reader now, the next version will be for Pillow plugin as well.
- top lvl images support(`burst`), see in examples. Only for reader now, the next version will be for Pillow plugin as well.
- method `thumbnails_all` returning an iterator for getting thumbnails in all images in `HeifFile`.

### Changed

- OPTIONS["avif"] and OPTIONS["strict"] replaced with `options` function, that returns `PyLibHeifOptions` class with those properties.
- if available, functions to check if image is supported `HEIF` will try to get 16 bytes instead of 12.

## [0.1.9 - 2022-03-10]

### Added

- Linux PyPy 3.7 & 3.8 wheels.
- IMPORTANT! `heif_filetype_*` constants will be deprecated in the future. Use `class HeifFiletype(IntEnum)`.
- IMPORTANT! `heif_brand_*` constants will be deprecated in the future. Use `class HeifBrand(IntEnum)`.
- Added `cfg_options` function, to change config when used not as `opener`. Look at `_options.py` for more info.
- OPTIONS: `strict` and `avif` - look at `reader.is_supported` function description.
- `class HeifErrorCode(IntEnum)` to use in custom exception handler.
- `class HeifColorspace(IntEnum)` instead of `heif_colorspace_*` constants.
- `class HeifChannel(IntEnum)` instead of `heif_channel_*` constants.
- `class HeifChroma(IntEnum)` instead of `heif_chroma_*` constants.
- A few examples of how to use.

### Changed

- `register_heif_opener` optionally accepts `**kwargs` as parameter, for overwriting values in config, when used as `opener`.
- `check_heif_magic` marked as deprecated. Use `is_supported` function instead.
- `check_heif` always return `HeifFiletype.NO` when there are less 12 bytes in input.
- Warning(`Unssuported HEIF... trying anyway`) was removed.
- `(Undecoded)HeifFile` and `HeifImageFile` classes was slightly changed(more consistent now). See the new description in README.md.
- Many other improvements and optimizations.
- When used as reader, functions `open_heif` and `read_heif` raise `HeifError` exception if file is not valid or broken.

### Fixed

- If `color_profile` is `prof` or `rICC` and data empty, `color_profile` will contain `data`=`None` instead of `color_profile`=`None`.
- `check_heif`, `is_supported`, `open_heif` and `read_heif` now preserves the file pointer, if input was a file handle.

## [0.1.8 - 2022-03-05]

### Added

- Ability to build from source on alpine with arm 7. Thanks to @aptalca

### Changed

- `HeifFile` `close` method now frees image decoded data.
- Code optimization.

## [0.1.7 - 2022-02-27]

### Added

- Added `manylinux2014_i686` wheels.
- Integration of PEP 517 in progress, added new instructions for building from source.

### Changed

- Making code cleaner, renamed cffi module from `pillow_heif.libheif` to `_pillow_heif_cffi`.
- libaom bumped from 3.2.0 to 3.3.0

### Fixed

- Fixed `AttributeError` when calling `Image.verify`. Thanks @zijian-hu for reporting.

## [0.1.6 - 2022-02-10]

### Added

- Windows binary wheels.
- More tests to `as_opener` module.
- Code coverage.

### Changed

- Using code formatting: black.
- Started changing build algorithms to support PEP 517.
- Speed optimizations and adjustments to `as_opener` module.
- Added `info[icc_profile]` to `HeifImageFile` when use it as `as_opener`.
- Adjustments to `reader` module:
- `pillow_heif.open` is in process of deprecation, still available, but you should use `open_heif` instead.
- `pillow_heif.check` is in process of deprecation, still available, but you should use `check_heif` instead.
- `pillow_heif.read` is in process of deprecation, still available, but you should use `read_heif` instead.

### Fixed

- Apple M1 binary wheels now build on Monterey 12.01 instead of 12.2.
- HeifError exception class now calls `super` to init all values.

## [0.1.5 - 2022-02-01]

### Added

- Apple M1 binary wheels.
- Alpine Linux binary wheels.
- More auto tests before publishing.

### Changed

- libaom bumped from 2.0.0 to 3.2.0

## [0.1.4 - 2021-11-05]

First normal working release.

### Added

- Python 3.10 wheels.
- Added `libaom` library to linux build.
- More tests.

### Changed

- Code refactoring, readme update.

### Fixed

- Bug with header check when used as plugin for Pillow with `as_opener` function. Thanks for this to @DimonLavron
