Benchmarks
==========

Creating two dataset image files:

.. code-block:: python

    def create_heif(size: tuple = None, thumb_boxes: list = None, n_images=1, **kwargs) -> BytesIO:
        if size is None:
            size = (512, 512)
        if thumb_boxes is None:
            thumb_boxes = []
        im_heif = pillow_heif.HeifFile()
        for i in range(n_images):
            im_heif.add_from_pillow(Image.effect_mandelbrot(size, (-3, -2.5, 2, 2.5), 100))
            size = (int(size[0] / 2), int(size[1] / 2))
            pillow_heif.add_thumbnails(im_heif[i], thumb_boxes)
        heif_buf = BytesIO()
        im_heif.save(heif_buf, quality=-1, **kwargs)
        return heif_buf

    _ = create_heif((4032, 3024), [1024, 512, 384, 256])
    with open("4032x3024.heic", "wb") as fh:
        fh.write(bytearray(_.getbuffer().tobytes()))

    _ = create_heif((3096, 2560), [512, 384, 256, 128, 64], 5)
    with open("3096x2560.heic", "wb") as fh:
        fh.write(bytearray(_.getbuffer().tobytes()))

    def f_to_bytesio(filepath):
        with open(Path(filepath), "rb") as fh:
            return BytesIO(fh.read())

    DATASET = [
        f_to_bytesio("4032x3024.heic"),
        f_to_bytesio("3096x2560.heic"),
    ]

Open benchmark
^^^^^^^^^^^^^^

.. code-block:: python

    def heif_open(dataset):
        for image_path in dataset:
            heif_file = pillow_heif.open_heif(image_path)
            for frame in heif_file:
                assert frame.size[0] > 0
                assert frame.bit_depth >= 8
                assert frame.mode == "RGBA" if frame.has_alpha else "RGB"


    def pil_open(dataset):
        for image_path in dataset:
            im = Image.open(image_path)
            for frame in ImageSequence.Iterator(im):
                assert frame.size[0] > 0
                assert frame.mode in ("RGBA", "RGB")

    @pytest.mark.benchmark(group="open")
    def test_heif_open(benchmark):
        benchmark.pedantic(heif_open, args=(DATASET,), iterations=2, rounds=500, warmup_rounds=1)


    @pytest.mark.benchmark(group="open")
    def test_pillow_open(benchmark):
        benchmark.pedantic(pil_open, args=(DATASET,), iterations=2, rounds=500, warmup_rounds=1)

Load benchmark
^^^^^^^^^^^^^^

.. code-block:: python

    def heif_load(dataset):
        for image_path in dataset:
            heif_file = pillow_heif.open_heif(image_path)
            for frame in heif_file:
                frame.load()


    def pil_load(dataset):
        for image_path in dataset:
            im = Image.open(image_path)
            for frame in ImageSequence.Iterator(im):
                frame.load()

    @pytest.mark.benchmark(group="load")
    def test_heif_load(benchmark):
        benchmark.pedantic(heif_load, args=(DATASET,), rounds=100, warmup_rounds=1)


    @pytest.mark.benchmark(group="load")
    def test_pillow_load(benchmark):
        benchmark.pedantic(pil_load, args=(DATASET,), rounds=100, warmup_rounds=1)

Save benchmark
^^^^^^^^^^^^^^

.. code-block:: python

    def heif_save(dataset):
        buf = BytesIO()
        for image_path in dataset:
            heif_file = pillow_heif.open_heif(image_path)
            heif_file.save(buf, quality=100)


    def pil_save(dataset):
        buf = BytesIO()
        for image_path in dataset:
            im = Image.open(image_path)
            im.save(buf, format="HEIF", quality=100, save_all=True)

    @pytest.mark.benchmark(group="save")
    def test_heif_save(benchmark):
        benchmark.pedantic(heif_save, args=(DATASET,), rounds=30, warmup_rounds=1)


    @pytest.mark.benchmark(group="save")
    def test_pillow_save(benchmark):
        benchmark.pedantic(pil_save, args=(DATASET,), rounds=30, warmup_rounds=1)

Results
^^^^^^^

.. note::

    There are different compilers used for Windows - MacOS - Linux builds, so this test did not show real CPU & OS performance.
    It is more for study and for understanding relative performance between builds.
    Results for `0.2.5` version  will be in brackets.

+-----------------------+--------------+----------------+----------------+
| Benchmark             | Mac Mini M1  | i9-10900 Linux | i7-9700 Win 10 |
+=======================+==============+================+================+
| heif_open             | 249(247) us  | 350(347) us    | 669(664) us    |
+-----------------------+--------------+----------------+----------------+
| pillow_open           | 268(266) us  | 404(401) us    | 674(669) us    |
+-----------------------+--------------+----------------+----------------+
| heif_load             | 225(225) ms  | 440(441) ms    | 573(577) ms    |
+-----------------------+--------------+----------------+----------------+
| pillow_load           | 240(255) ms  | 460(480) ms    | 590(632) ms    |
+-----------------------+--------------+----------------+----------------+
| heif_save             | 4.53(4.56) s | 3.27(3.29) s   | 2.56(2.65) s   |
+-----------------------+--------------+----------------+----------------+
| pillow_save           | 4.66(4.71) s | 3.50(3.53) s   | 2.94(3.02) s   |
+-----------------------+--------------+----------------+----------------+

Version ``0.5.0`` is faster in both decoding and encoding.
