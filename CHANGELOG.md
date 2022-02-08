# Changelog

All notable changes to this project will be documented in this file.

## [0.1.6 - 2022-02-10]

### Added

- Windows binary wheels.

### Changed

- Using code formatting: black.
- Started changing build algorithms to support PEP 517.

### Fixed

- Apple M1 binary wheels now build on Monterey 12.01 instead of 12.2.

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
