import sys
from os import path
from subprocess import run
from time import perf_counter

import matplotlib.pyplot as plt
from cpuinfo import get_cpu_info

VERSIONS = ["0.1.6", "0.1.11", "0.2.1", "0.2.5", "0.3.2", "0.4.0", "0.5.1", "0.6.0", "0.7.0", "0.7.2", "0.8.0", "0.9.0"]
N_ITER_SMALL = 100
N_ITER_LARGE = 50


def measure_decode(image, n_iterations, decode_threads=4):
    measure_file = path.join(path.dirname(path.abspath(__file__)), "measure_decode.py")
    cmd = f"{sys.executable} {measure_file} {n_iterations} {image} {decode_threads}".split()
    start_time = perf_counter()
    run(cmd, check=True)
    total_time = perf_counter() - start_time
    return total_time / n_iterations


def plot_large_by_threads(clr, n_threads):
    plt.plot(
        "0.9.0",
        measure_decode("image_large.heic", N_ITER_LARGE, decode_threads=n_threads),
        color=clr,
        label=f"n_threads={n_threads}",
        marker="x",
    )


if __name__ == "__main__":
    tests_images_path = path.join(path.dirname(path.dirname(path.abspath(__file__))), "tests/images/heif_other")
    arrow_image_path = path.join(tests_images_path, "arrow.heic")
    cat_image_path = path.join(tests_images_path, "cat.hif")
    arrow_image_results = []
    cat_image_results = []
    small_image_results = []
    large_image_results = []
    for i, v in enumerate(VERSIONS):
        run(f"{sys.executable} -m pip install pillow-heif=={v}".split(), check=True)
        arrow_image_results.append(measure_decode(arrow_image_path, N_ITER_SMALL))
        cat_image_results.append(measure_decode(cat_image_path, N_ITER_SMALL))
        small_image_results.append(measure_decode("image_small.heic", N_ITER_SMALL))
        large_image_results.append(measure_decode("image_large.heic", N_ITER_LARGE))
    fig, ax = plt.subplots()
    ax.plot(VERSIONS, arrow_image_results, label="arrow image")
    ax.plot(VERSIONS, cat_image_results, label="cat image")
    ax.plot(VERSIONS, small_image_results, label="small image")
    ax.plot(VERSIONS, large_image_results, label="large image")
    colour = plt.gca().lines[-1].get_color()
    plot_large_by_threads(colour, 1)
    plot_large_by_threads(colour, 2)
    plot_large_by_threads(colour, 8)
    plt.ylabel("time to decode(s)")
    if sys.platform.lower() == "darwin":
        _os = "macOS"
    elif sys.platform.lower() == "win32":
        _os = "Windows"
    else:
        _os = "Linux"
    plt.xlabel(f"{_os} - {get_cpu_info()['brand_raw']}")
    ax.legend()
    plt.savefig(f"results_decode_{_os}.png")
