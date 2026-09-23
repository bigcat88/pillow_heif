import io
import os
import shutil
import subprocess
import sys
from io import BytesIO
from pathlib import Path
from threading import Thread
from unittest import mock

import helpers
import pytest
from PIL import Image, ImageChops, ImageSequence, UnidentifiedImageError

import pillow_heif
from pillow_heif import misc

os.chdir(os.path.dirname(os.path.abspath(__file__)))

pillow_heif.register_heif_opener()


HEAD_SIZE = misc.FileSource.HEAD_SIZE


@pytest.fixture
def file_reads():
    reads = []
    original_read_at = misc.FileSource.read_at
    original_read_head = misc.FileSource.read_head

    def read_at(self, offset, length):
        data = original_read_at(self, offset, length)
        reads.append((offset, len(data)))
        return data

    def read_head(self, fp):
        n_reads = len(reads)
        head = original_read_head(self, fp)
        del reads[n_reads:]  # how much of the head Pillow has in the buffer of the file depends on the Python version
        reads.append((0, len(head)))
        return head

    with (
        mock.patch.object(misc.FileSource, "read_at", read_at),
        mock.patch.object(misc.FileSource, "read_head", read_head),
    ):
        yield reads


def open_from_memory(path):
    return Image.open(BytesIO(Path(path).read_bytes()))


def info_without_depth(im):
    return {k: v for k, v in im.info.items() if k != "depth_images"}


def assert_each_byte_read_once(file_reads, path):
    position = 0
    for offset, length in sorted(file_reads):
        assert offset == position
        position += length
    assert position == os.path.getsize(path)


@pytest.mark.parametrize(
    "path,expected_reads",
    (
        ("images/heif_other/pug.heic", [(0, HEAD_SIZE)]),
        ("images/heif_other/cat.hif", [(0, HEAD_SIZE)]),
        ("images/heif_special/xiaomi.heic", [(0, HEAD_SIZE), (HEAD_SIZE, 173693)]),  # 188 KB of EXIF
    ),
)
def test_metadata_is_read_without_the_image_data(file_reads, path, expected_reads):
    with Image.open(Path(path)) as im:
        exif = im.getexif()
        assert file_reads == expected_reads
        im_memory = open_from_memory(path)
        assert exif == im_memory.getexif()
        assert info_without_depth(im) == info_without_depth(im_memory)
        assert (im.size, im.mode, im.n_frames) == (im_memory.size, im_memory.mode, im_memory.n_frames)
    assert file_reads == expected_reads


@pytest.mark.parametrize("path", ("images/heif_other/pug.heic", "images/heif_other/cat.hif"))
def test_load_reads_each_byte_once(file_reads, path):
    im = Image.open(Path(path))
    im.load()
    assert_each_byte_read_once(file_reads, path)
    assert im.tobytes() == open_from_memory(path).tobytes()


def test_file_object_is_read_at_once(file_reads):
    with open("images/heif_other/pug.heic", "rb") as fp:
        im = Image.open(fp)
    im.load()  # `fp` is closed already
    assert im.tobytes() == open_from_memory("images/heif_other/pug.heic").tobytes()
    assert not file_reads


def test_small_file_is_read_at_once(file_reads):
    path = "images/heif/zPug_3.heic"
    im = Image.open(Path(path))
    assert file_reads == [(0, os.path.getsize(path))]
    for frame in range(im.n_frames):
        im.seek(frame)
        im.load()
    assert file_reads == [(0, os.path.getsize(path))]


def test_load_after_close(file_reads, tmp_path, monkeypatch):
    with Image.open("images/heif_other/pug.heic") as im:
        pass
    monkeypatch.chdir(tmp_path)  # the path was relative
    im.load()
    monkeypatch.undo()
    assert im.tobytes() == open_from_memory("images/heif_other/pug.heic").tobytes()
    assert sum(length for _, length in file_reads) == os.path.getsize("images/heif_other/pug.heic")


def test_file_changed_after_close(tmp_path):
    path = tmp_path / "pug.heic"
    shutil.copy("images/heif_other/pug.heic", path)
    with Image.open(path) as im:
        pass
    with open(path, "ab") as fp:
        fp.write(b"\0")
    with pytest.raises(OSError, match="was changed after it was opened"):
        im.load()


def test_file_attributes_changed_after_close(tmp_path):
    path = tmp_path / "pug.heic"
    shutil.copy("images/heif_other/pug.heic", path)
    with Image.open(path) as im:
        pass
    os.chmod(path, 0o600)  # these change the change time of the file, not its data
    os.link(path, tmp_path / "link.heic")
    im.load()
    assert im.tobytes() == open_from_memory("images/heif_other/pug.heic").tobytes()


def test_file_removed_after_close(tmp_path):
    path = tmp_path / "pug.heic"
    shutil.copy("images/heif_other/pug.heic", path)
    with Image.open(path) as im:
        pass
    path.unlink()
    with pytest.raises(FileNotFoundError):
        im.load()


def test_file_truncated_after_open(tmp_path):
    path = tmp_path / "pug.heic"
    shutil.copy("images/heif_other/pug.heic", path)
    with Image.open(path) as im:
        os.truncate(path, 300000)
        with pytest.raises(OSError, match="was changed after it was opened"):
            im.load()


def test_file_rewritten_before_load(tmp_path):
    path = tmp_path / "pug.heic"
    shutil.copy("images/heif_other/pug.heic", path)
    with Image.open(path) as im:
        path.write_bytes(Path("images/heif_other/cat.hif").read_bytes())  # the same file, Pillow still has it open
        with pytest.raises(OSError, match="was changed after it was opened"):
            im.load()


@pytest.mark.skipif(os.name == "nt", reason="a file cannot be removed while Pillow has it open on Windows")
def test_file_replaced_before_load(tmp_path):
    path = tmp_path / "pug.heic"
    shutil.copy("images/heif_other/pug.heic", path)
    with Image.open(path) as im:
        shutil.copy("images/heif_other/cat.hif", tmp_path / "cat.hif")
        os.replace(tmp_path / "cat.hif", path)
        im.load()
        assert im.tobytes() == open_from_memory("images/heif_other/pug.heic").tobytes()


def test_file_libheif_reads_only_from_memory():
    path = "images/heif_special/big_ftyp.heic"  # the `ftyp` box is bigger than the first 1 KB libheif requests
    with Image.open(Path(path)) as im:
        assert im.tobytes() == open_from_memory(path).tobytes()


def test_file_needed_in_many_parts(file_reads, tmp_path):
    path = tmp_path / "boxes.heic"  # libheif reads the header of every box: each part it needs costs a new parse
    path.write_bytes(Path("images/heif/zPug_3.heic").read_bytes() + b"\0\0\0\x08free" * 2_000_000)
    with Image.open(path) as im:
        assert len(file_reads) <= 6  # the first 128 KB, four parts, the rest of the file
        assert im.tobytes() == open_from_memory(path).tobytes()


def test_file_of_a_file_system_in_memory():
    class InMemoryFile(io.BufferedIOBase):  # as pyfakefs does: the descriptor belongs to another file
        def __init__(self, data, fileno):
            super().__init__()
            self._data = BytesIO(data)
            self._fileno = fileno

        def fileno(self):
            return self._fileno

        def readable(self):
            return True

        def seekable(self):
            return True

        def read(self, size=-1):
            return self._data.read(size)

        def seek(self, offset, whence=0):
            return self._data.seek(offset, whence)

        def tell(self):
            return self._data.tell()

    with open("images/heif_other/cat.hif", "rb") as other:
        fp = InMemoryFile(Path("images/heif_other/pug.heic").read_bytes(), other.fileno())
        heif_file = pillow_heif.HeifFile(fp, lazy_read=True, filename="pug.heic")
        assert heif_file.size == open_from_memory("images/heif_other/pug.heic").size


def test_file_position_without_pread(monkeypatch):
    monkeypatch.delattr(os, "pread", raising=False)  # as on Windows
    with Image.open(Path("images/heif_special/xiaomi.heic")) as im:  # its EXIF ends after the first 128 KB
        assert im.fp.tell() == 0


def test_read_error_while_decoding_a_thumbnail():
    with Image.open(Path("images/heif_other/nokia/stereo_1200x800.heic")) as im:
        with (
            mock.patch.object(misc.FileSource, "read_at", side_effect=OSError("connection lost")),
            pytest.raises(OSError, match="connection lost"),
        ):
            im.draft(None, (240, 160))
        assert im.draft(None, (240, 160)) == ("RGB", (0, 0, 480, 320))


@pytest.mark.parametrize("path", (os.devnull, "empty"))
def test_special_files_are_read_at_once(file_reads, tmp_path, path):
    if path == "empty":
        path = tmp_path / "empty.heic"
        path.write_bytes(b"")
    with open(path, "rb") as fp, pytest.raises(ValueError):
        pillow_heif.HeifFile(fp, lazy_read=True, filename=str(path))
    assert not file_reads


def test_read_error_while_opening():
    original = misc.FileSource.read_at

    def read_at(self, offset, length):
        if offset >= HEAD_SIZE:
            raise OSError("connection lost")
        return original(self, offset, length)

    with mock.patch.object(misc.FileSource, "read_at", read_at):
        Image.open(Path("images/heif_other/pug.heic")).close()  # everything is in the first part of the file
        with pytest.raises(UnidentifiedImageError):
            Image.open(Path("images/heif_special/xiaomi.heic"))


def test_depth_image_outlives_the_image(file_reads):
    path = "images/heif_other/pug.heic"
    with Image.open(Path(path)) as im:
        depth_image = im.info["depth_images"][0]
    del im
    depth_memory = open_from_memory(path).info["depth_images"][0]
    assert depth_image.to_pillow().tobytes() == depth_memory.to_pillow().tobytes()
    assert_each_byte_read_once(file_reads, path)


def test_frames_after_the_file_is_closed(file_reads):
    path = "images/heif_other/nokia/bird_burst.heic"
    im = Image.open(Path(path))
    im_memory = open_from_memory(path)
    assert im.n_frames == im_memory.n_frames == 4
    for frame in range(im.n_frames):
        im.seek(frame)
        im_memory.seek(frame)
        assert im.tobytes() == im_memory.tobytes()
        assert im.fp is None
    assert sum(length for _, length in file_reads) == os.path.getsize(path)


def test_thumbnail_load_reads_the_rest_of_the_file(file_reads):
    path = "images/heif_special/200MP.heic"
    max_image_pixels = Image.MAX_IMAGE_PIXELS
    try:
        Image.MAX_IMAGE_PIXELS = None
        im = Image.open(Path(path))
        assert im.draft(None, (256, 256)) == ("RGB", (0, 0, 384, 512))
        im_memory = open_from_memory(path)
        im_memory.draft(None, (256, 256))
        assert im.tobytes() == im_memory.tobytes()
    finally:
        Image.MAX_IMAGE_PIXELS = max_image_pixels
    assert_each_byte_read_once(file_reads, path)


@pytest.mark.skipif(not helpers.hevc_enc(), reason="Requires HEVC encoder.")
def test_save_over_the_file_after_thumbnail(tmp_path):
    path = tmp_path / "frames.heic"
    frames = [  # the noise makes the frames bigger than the parts of the file that are read for the thumbnail
        ImageChops.add(
            Image.linear_gradient("L").rotate(90 * i).resize((512, 384)), Image.effect_noise((512, 384), 32), 1, -128
        ).convert("RGB")
        for i in range(3)
    ]
    frames[0].save(path, save_all=True, append_images=frames[1:], thumbnails=[256], quality=90)
    originals = [frame.copy() for frame in ImageSequence.Iterator(open_from_memory(path))]
    im = Image.open(path)
    im.thumbnail((64, 48))  # decodes the embedded thumbnail of the first frame
    im.save(path, save_all=True)  # Pillow empties the file before the frames are decoded
    with Image.open(path) as saved:
        assert saved.n_frames == 3
        for frame in (1, 2):  # these are read from the file only when they are saved
            saved.seek(frame)
            helpers.assert_image_similar(saved.convert("RGB"), originals[frame], 20)


def test_images_of_one_file_decoded_in_threads(file_reads):
    path = "images/heif_other/nokia/bird_burst.heic"
    with open(path, "rb") as fp:
        heif_file = pillow_heif.HeifFile(fp, lazy_read=True, filename=path)
        assert file_reads == [(0, HEAD_SIZE)]
        decoded = {}

        def decode(index):
            decoded[index] = bytes(heif_file[index].data)

        threads = [Thread(target=decode, args=(i,)) for i in range(len(heif_file))]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    heif_file_memory = pillow_heif.open_heif(path)
    assert [decoded[i] for i in range(len(heif_file))] == [bytes(i.data) for i in heif_file_memory]
    assert file_reads == [(0, HEAD_SIZE), (HEAD_SIZE, os.path.getsize(path) - HEAD_SIZE)]


DECODE_WHILE_PARSING = """
import sys
import threading

from PIL import Image

import pillow_heif

pillow_heif.register_heif_opener()
errors = []
threading.excepthook = lambda args: errors.append(repr(args.exc_value))


def decode(path):
    for _ in range(3):
        with Image.open(path) as im:
            im.load()


def parse(path):
    while any(thread.is_alive() for thread in decoders):
        with Image.open(path) as im:
            im.getexif()


decoders = [threading.Thread(target=decode, args=(sys.argv[1],)) for _ in range(2)]
parsers = [threading.Thread(target=parse, args=(sys.argv[2],)) for _ in range(2)]
for thread in decoders + parsers:
    thread.start()
for thread in decoders + parsers:
    thread.join()
sys.exit("\\n".join(errors) or 0)
"""


def test_file_parsed_while_another_is_decoded():
    # libheif calls the reader of a file that is decoded without the GIL, and holds its lock for reading item data;
    # a parse in another thread holds the GIL and waits for that lock: a reader that needs the GIL hangs (PyPy)
    decoded = str(Path("images/heif_other/cat.hif").resolve())  # a grid, libheif decodes its tiles in threads
    parsed = str(Path("images/heif_special/xiaomi.heic").resolve())  # its EXIF is read at open
    result = subprocess.run(
        [sys.executable, "-c", DECODE_WHILE_PARSING, decoded, parsed], capture_output=True, text=True, timeout=60
    )
    assert result.returncode == 0, result.stderr
