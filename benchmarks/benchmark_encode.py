import sys
from os import path
from subprocess import run
from time import perf_counter

import matplotlib.pyplot as plt
from cpuinfo import get_cpu_info

VERSIONS = ["0.5.1", "0.6.1", "0.7.2", "0.8.0", "0.9.3", "0.10.0"]
N_ITER = 30


def measure_encode(image, n_iterations):
    measure_file = path.join(path.dirname(path.abspath(__file__)), "measure_encode.py")
    cmd = f"{sys.executable} {measure_file} {n_iterations} {image}".split()
    start_time = perf_counter()
    run(cmd, check=True)
    total_time = perf_counter() - start_time
    return total_time / n_iterations


if __name__ == "__main__":
    rgba_image_results = []
    rgb_image_results = []
    la_image_results = []
    l_image_results = []
    pug_image_results = []
    for i, v in enumerate(VERSIONS):
        run(f"{sys.executable} -m pip install pillow-heif=={v}".split(), check=True)
        rgba_image_results.append(measure_encode("RGBA", N_ITER))
        rgb_image_results.append(measure_encode("RGB", N_ITER))
        la_image_results.append(measure_encode("LA", N_ITER))
        l_image_results.append(measure_encode("L", N_ITER))
        pug_image_results.append(measure_encode("PUG", N_ITER))
    fig, ax = plt.subplots()
    ax.plot(VERSIONS, rgba_image_results, label="RGBA image")
    ax.plot(VERSIONS, rgb_image_results, label="RGB image")
    ax.plot(VERSIONS, la_image_results, label="LA image")
    ax.plot(VERSIONS, l_image_results, label="L image")
    ax.plot(VERSIONS, pug_image_results, label="PUG image(RGB)")
    plt.ylabel("time to encode(s)")
    if sys.platform.lower() == "darwin":
        _os = "macOS"
    elif sys.platform.lower() == "win32":
        _os = "Windows"
    else:
        _os = "Linux"
    plt.xlabel(f"{_os} - {get_cpu_info()['brand_raw']}")
    ax.legend()
    plt.savefig(f"results_encode_{_os}.png")
