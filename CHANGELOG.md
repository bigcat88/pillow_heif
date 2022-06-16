# Changelog

All notable changes to this project will be documented in this file.

## [0.3.1 - 2022-06-17]

### Added

- (Heif) - `HeifFile` gets `images: List[HeifImage]` and alternative method of changing order of images by editing it.
- (HeifImagePlugin) - `info` image dictionary can be now edited in place and it will be saved for image sequences.

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

### Fixed

## [0.2.4 - 2022-05-18]

### Added

- (HeifImagePlugin) - saving of XMP tags from PNG.
- Benchmarks page to docs.

### Changed

- Added option `ctx_in_memory`, default=True. Benchmarks showed that versions 0.1.x which worked like this, was much faster.
This will not affect any user code, changes are internal.

### Fixed

- (HeifImagePlugin) - XMP Orientation tag.
- (HeifImagePlugin, encoder) - L and LA color modes. #23 (@Jarikf)

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
- (Heif) - HeifImage.chroma and HeifImage.color property now avalaible before image load, right after `open`.

## [0.2.2 - 2022-04-23]

### Added

- PyPy 3.9 wheels.
- (HeifImagePlugin, Heif) `append_images` parameter to `save` methods.
- (HeifImagePlugin) - `import pillow_heif.HeifImagePlugin` for automatic Pillow plugin registration(as alternative to calling `register_heif_opener`).
- (HeifImagePlugin, Heif) `quality` can be now `-1` which indicates a lossless encoding.
- (HeifImagePlugin) - `getxmp` method. Works the same way like in Pillow's `PngImagePlugin` | `JpegImagePlugin`.
- (Heif) - added raw `xml` as `info["xml"]` and public function `pillow_heif.getxmp`(the same as for `HeifImagePlugin`)

### Changed

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
- All thumbnails encoding features reworked, to simplify api. See `add_thumbnails` methods in `HeifFile` and `HeifImage` classes.

### Fixed

- (HeifImagePlugin) Fixed palette images with bytes transparency conversion. #21 (@Jarikf)
- (Heif) Raises `ValueError` when trying to save empty(no images) file.
- (HeifImagePlugin) Skips images with sizes = `0` during save, if there is no images, raise `ValueError`.
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
- in future there will be much less changes to api, this project goes to `stable` version from now.

### Fixed

- Speed and memory optimisations.

## [0.1.11 - 2022-03-24]

### Added

- Linux aarch64 PyPy 3.7 & 3.8 wheels.
- wrapper for libheif function `get_file_mimetype`.
- `burst`(container) image support(`ImageSequence`) for `heic` and `hif` when using as a pillow plugin.
- convert to jpg example for both `reader` and `plugin` use.
- in addition to iterator to loop throw all images, `(Undecoded)``HeifFile` class now support access images by index.

### Changed

- `heif_brand_*` constants was removed, as mentioned in changes for 0.1.9 version.

### Fixed

- memory leak when working with thumbnails, now properly releases thumbnail handle.
- rare bug with garbage collector for PyPy.
- `as_opener` register `image/heic` mimetype in addition to `image/heif`.
- `as_opener` also registers `.heif` extension, thanks @dust-to-dust for pointing that.
- `as_opener` sets `orientation` tag to `1` from `Exif` to not rotate image twice(`libheif` already do transforms)
- for `reader` you can do that manually if needed, with new `reset_orientation` function.

## [0.1.10 - 2022-03-17]

### Added

- macOS Intel PyPy3.7 & PyPy3.8 v7.3 wheels.
- class `HeifCompressionFormat(IntEnum)`. `have_decoder_for_format` and `have_encoder_for_format` functions.
- function `libheif_info` that returns dictionary with version and avalaible (en)(de)coders.
- class `HeifThumbnail` for thumbnails, see in examples. Only for reader now, in next version will be for Pillow plugin as well.
- top lvl images support(`burst`), see in examples. Only for reader now, in next version will be for Pillow plugin as well.
- method `thumbnails_all` returning an iterator for getting thumbnails in all images in `HeifFile`.

### Changed

- OPTIONS["avif"] and OPTIONS["strict"] replaced with `options` function, that returns `PyLibHeifOptions` class with that properties.
- if avalaible, functions to check if image is supported `HEIF` will try get 16 bytes instead of 12.

### Fixed

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
- A few examples how to use.

### Changed

- `register_heif_opener` optionally accepts `**kwargs` as parameter, for overwriting values in config, when used as `opener`.
- `check_heif_magic` marked as deprecated. Use `is_supported` function instead.
- `check_heif` always return `HeifFiletype.NO` when there are less 12 bytes in input.
- Warning(`Unssuported HEIF... trying anyway`) was removed.
- `(Undecoded)HeifFile` and `HeifImageFile` classes was slightly changed(more consistent now). See new description in README.md.
- Many other improvements and optimizations.
- When used as reader, functions `open_heif` and `read_heif` raise `HeifError` exception if file is not valid or broken.

### Fixed

- If `color_profile` is `prof` or `rICC` and data empty, `color_profile` will contain `data`=`None` instead of `color_profile`=`None`.
- `check_heif`, `is_supported`, `open_heif` and `read_heif` now preserves file pointer, if input was file handle.

## [0.1.8 - 2022-03-05]

### Added

- Ability to build from source on alpine with arm 7. Thanks to @aptalca

### Changed

- `HeifFile` `close` method now frees image decoded data.
- Code optimization.

### Fixed

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
- Linux binary wheels for Python 3.6(this is last release for Python 3.6).

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

- Python 3.6 is no longer supported.
- libaom bumped from 2.0.0 to 3.2.0

### Fixed

## [0.1.4 - 2021-11-05]

### Added

- GitHub build Actions now use cache.
- Added `libaom` library to linux build.
- More tests.

### Changed

- Code refactoring, readme update.

### Fixed

- Bug with header check when used as plugin for Pillow with `as_opener` function. Thanks for this to @DimonLavron

## [0.1.3 - 2021-10-25]

### Added

- Python 3.10 wheels.
- New function pillow_heif.open() added.(by @homm, more info: https://github.com/carsales/pyheif/pull/55)

### Changed

- Some speed optimizations.(by @homm)

## [0.1.2 - 2021-09-15]

### Fixed

- Fixed empty color profiles work and for images with no exif.

## [0.1.1 - 2021-09-12]

### Added

### Changed

- First working release.
- libde version=1.0.8
- x265 version=3.5
- libheif version=1.12.0

### Fixed
