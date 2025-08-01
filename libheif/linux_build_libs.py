"""File containing code to build Linux libraries for LibHeif and the LibHeif itself."""

import sys
from os import chdir, environ, getcwd, getenv, makedirs, mkdir, path, remove
from platform import machine
from re import IGNORECASE, MULTILINE, match, search
from subprocess import DEVNULL, PIPE, STDOUT, CalledProcessError, TimeoutExpired, run

# 1
BUILD_DIR = environ.get("BUILD_DIR", "/tmp/ph_build_stuff")
INSTALL_DIR_LIBS = environ.get("INSTALL_DIR_LIBS", "/usr")
PH_LIGHT_VERSION = sys.maxsize <= 2**32 or getenv("PH_LIGHT_ACTION", "0") != "0"

LIBX265_URL = "https://bitbucket.org/multicoreware/x265_git/downloads/x265_4.1.tar.gz"
LIBDE265_URL = "https://github.com/strukturag/libde265/releases/download/v1.0.16/libde265-1.0.16.tar.gz"
LIBHEIF_URL = "https://github.com/strukturag/libheif/releases/download/v1.20.1/libheif-1.20.1.tar.gz"


def download_file(url: str, out_path: str) -> bool:
    n_download_clients = 2
    for _ in range(2):
        try:
            run(
                ["wget", "-q", "--no-check-certificate", url, "-O", out_path],
                timeout=90,
                stderr=DEVNULL,
                stdout=DEVNULL,
                check=True,
            )
            return True
        except (CalledProcessError, TimeoutExpired):
            break
        except FileNotFoundError:
            n_download_clients -= 1
            break
    for _ in range(2):
        try:
            run(["curl", "-L", url, "-o", out_path], timeout=90, stderr=DEVNULL, stdout=DEVNULL, check=True)
            return True
        except (CalledProcessError, TimeoutExpired):
            break
        except FileNotFoundError:
            n_download_clients -= 1
            break
    if not n_download_clients:
        raise OSError("Both curl and wget cannot be found.")
    return False


def download_extract_to(url: str, out_path: str, strip: bool = True):
    makedirs(out_path, exist_ok=True)
    archive_path = path.join(out_path, "download.tar.gz")
    download_file(url, archive_path)
    tar_cmd = f"tar -xf {archive_path} -C {out_path}"
    if strip:
        tar_cmd += " --strip-components 1"
    run(tar_cmd.split(), check=True)
    remove(archive_path)


def tool_check_version(name: str, min_version: str) -> bool:
    try:
        _ = run([name, "--version"], stdout=PIPE, stderr=DEVNULL, check=True)
    except (CalledProcessError, FileNotFoundError):
        return False
    v_regexp = r"version\s*(\d+(\.\d+){2})" if name == "nasm" else r"(\d+(\.\d+){2})$"  # cmake
    m_groups = search(v_regexp, _.stdout.decode("utf-8"), flags=MULTILINE + IGNORECASE)
    if m_groups is None:
        return False
    current_version = tuple(map(int, str(m_groups.groups()[0]).split(".")))
    min_version = tuple(map(int, min_version.split(".")))
    if current_version >= min_version:
        print(f"Tool {name} with version {m_groups.groups()[0]} satisfy requirements.", flush=True)
        return True
    return False


def check_install_nasm(version: str):
    if not match(r"(i[3-6]86|x86_64)$", machine()):
        return True
    if tool_check_version("nasm", version):
        return True
    print(f"Can not find `nasm` with version >={version}, installing...")
    tool_path = path.join(BUILD_DIR, "nasm")
    if path.isdir(tool_path):
        print("Cache found for nasm", flush=True)
        chdir(tool_path)
    else:
        download_extract_to(f"https://www.nasm.us/pub/nasm/releasebuilds/{version}/nasm-{version}.tar.gz", tool_path)
        chdir(tool_path)
        run(["./configure"], check=True)
        run("make".split(), check=True)
    run("make install".split(), check=True)
    run("nasm --version".split(), check=True)
    run(f"chmod -R 774 {tool_path}".split(), check=True)
    return True


def is_musllinux() -> bool:
    _ = run("ldd --version".split(), stdout=PIPE, stderr=STDOUT, check=False)
    return bool(_.stdout and _.stdout.decode("utf-8").find("musl") != -1)


def is_library_installed(name: str) -> bool:
    if name.find("main") != -1 and name.find("reference") != -1:
        raise Exception("`name` param can not contain `main` and `reference` substrings.")
    result = run(f"gcc -l{name}".split(), stdout=PIPE, stderr=STDOUT, check=False)
    if result.stdout:
        decoded_result = result.stdout.decode("utf-8")
        if decoded_result.find("main") != -1 and decoded_result.find("reference") != -1:
            return True
    return False


def run_print_if_error(args) -> None:
    _ = run(args, stdout=PIPE, stderr=STDOUT, check=False)
    if _.returncode != 0:
        print(_.stdout.decode("utf-8"), flush=True)
        raise ChildProcessError(f"Failed: {args}")


def build_lib_linux(url: str, name: str):
    lib_path = path.join(BUILD_DIR, name)
    if path.isdir(lib_path):
        print(f"Cache found for {name}", flush=True)
        chdir(path.join(lib_path, "build")) if name != "x265" else chdir(lib_path)
    else:
        hide_build_process = True
        script_dir = path.dirname(path.abspath(__file__))
        linux_dir = path.join(script_dir, "linux")  # noqa
        if name == "x265":
            download_extract_to(url, lib_path)
            chdir(lib_path)
        else:
            build_path = path.join(lib_path, "build")
            makedirs(build_path)
            download_extract_to(url, lib_path)
            if name == "libde265":  # noqa
                chdir(lib_path)
                # for patch in (
                #     "libde265/CVE-2022-1253.patch",
                # ):
                #     patch_path = path.join(linux_dir, patch)
                #     run(f"patch -p 1 -i {patch_path}".split(), check=True)
            elif name == "libheif":
                chdir(lib_path)
                # for patch in (
                #     "libheif/001-void-unused-variable.patch",
                # ):
                #     patch_path = path.join(linux_dir, patch)
                #     run(f"patch -p 1 -i {patch_path}".split(), check=True)
            chdir(build_path)
        print(f"Preconfiguring {name}...", flush=True)
        if name == "x265":
            cmake_high_bits = "-DHIGH_BIT_DEPTH=ON -DEXPORT_C_API=OFF".split()
            cmake_high_bits += "-DENABLE_SHARED=OFF -DENABLE_CLI=OFF".split()
            mkdir("12bit")
            mkdir("10bit")
            chdir("10bit")
            run("cmake ./../source -DENABLE_HDR10_PLUS=ON".split() + cmake_high_bits, check=True)
            run_print_if_error("make -j4".split())
            run("mv libx265.a ../libx265_main10.a".split(), check=True)
            chdir("../12bit")
            run(["cmake", "./../source", "-DMAIN12=ON", *cmake_high_bits], check=True)
            run_print_if_error("make -j4".split())
            run("mv libx265.a ../libx265_main12.a".split(), check=True)
            chdir("..")
            cmake_args = f"-DCMAKE_INSTALL_PREFIX={INSTALL_DIR_LIBS} ./source".split()
            cmake_args += ["-G", "Unix Makefiles"]
            cmake_args += "-DLINKED_10BIT=ON -DLINKED_12BIT=ON -DEXTRA_LINK_FLAGS=-L.".split()
            cmake_args += "-DEXTRA_LIB='x265_main10.a;x265_main12.a'".split()
        else:
            cmake_args = f"-DCMAKE_INSTALL_PREFIX={INSTALL_DIR_LIBS} ..".split()
            cmake_args += ["-DCMAKE_BUILD_TYPE=Release"]
            if name == "libheif":
                cmake_args += (
                    "-DWITH_OPENJPH_DECODER=OFF "
                    "-DWITH_OPENJPH_ENCODER=OFF "
                    "-DWITH_HEADER_COMPRESSION=OFF "
                    "-DWITH_LIBDE265=ON "
                    "-DWITH_LIBDE265_PLUGIN=OFF "
                    "-DWITH_X265=ON "
                    "-DWITH_X265_PLUGIN=OFF "
                    "-DWITH_AOM_DECODER=OFF "
                    "-DWITH_AOM_DECODER_PLUGIN=OFF "
                    "-DWITH_AOM_ENCODER=OFF "
                    "-DWITH_AOM_ENCODER_PLUGIN=OFF "
                    "-DWITH_RAV1E=OFF "
                    "-DWITH_RAV1E_PLUGIN=OFF "
                    "-DWITH_DAV1D=OFF "
                    "-DWITH_DAV1D_PLUGIN=OFF "
                    "-DWITH_SvtEnc=OFF "
                    "-DWITH_SvtEnc_PLUGIN=OFF "
                    "-DWITH_KVAZAAR=OFF "
                    "-DWITH_KVAZAAR_PLUGIN=OFF "
                    "-DWITH_JPEG_DECODER=OFF "
                    "-DWITH_JPEG_ENCODER=OFF "
                    "-DWITH_OpenJPEG_DECODER=OFF "
                    "-DWITH_OpenJPEG_ENCODER=OFF "
                    "-DENABLE_PLUGIN_LOADING=OFF "
                    "-DWITH_LIBSHARPYUV=OFF "
                    "-DWITH_EXAMPLES=OFF "
                    "-DBUILD_TESTING=OFF".split()
                )
                hide_build_process = False
                if is_musllinux():
                    cmake_args += [f"-DCMAKE_INSTALL_LIBDIR={INSTALL_DIR_LIBS}/lib"]
        run(["cmake", *cmake_args], check=True)
        print(f"{name} configured. building...", flush=True)
        if hide_build_process:
            run_print_if_error("make -j4".split())
        else:
            run("make -j4".split(), check=True)
        print(f"{name} build success.", flush=True)
    run("make install".split(), check=True)
    if is_musllinux():
        run(f"ldconfig {INSTALL_DIR_LIBS}/lib".split(), check=True)
    else:
        run("ldconfig", check=True)


def build_libs() -> None:
    original_dir = getcwd()
    try:
        if not tool_check_version("cmake", "3.16.3"):
            raise ValueError("Can not find `cmake` with version >=3.16.3")
        if not is_library_installed("x265"):
            if not PH_LIGHT_VERSION:
                if not check_install_nasm("2.15.05"):
                    raise ValueError("Can not find/install `nasm` with version >=2.15.05")
                build_lib_linux(LIBX265_URL, "x265")
        else:
            print("x265 already installed.")
        if not is_library_installed("libde265") and not is_library_installed("de265"):
            build_lib_linux(LIBDE265_URL, "libde265")
        else:
            print("libde265 already installed.")
        build_lib_linux(LIBHEIF_URL, "libheif")
    finally:
        chdir(original_dir)


if __name__ == "__main__":
    build_libs()
