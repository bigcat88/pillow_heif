import sys
from os import chdir, environ, getcwd, getenv, makedirs, mkdir, path
from platform import machine
from subprocess import PIPE, STDOUT, run

from libheif import linux_build_tools

BUILD_DIR_PREFIX = environ.get("BUILD_DIR_PREFIX", "/tmp/pillow_heif")
BUILD_DIR_LIBS = path.join(BUILD_DIR_PREFIX, "build-stuff")
INSTALL_DIR_LIBS = environ.get("INSTALL_DIR_LIBS", "/usr")


PH_LIGHT_VERSION = sys.maxsize <= 2**32 or getenv("PH_LIGHT_ACTION", "0") != "0"


def is_musllinux() -> bool:
    _ = run("ldd --version".split(), stdout=PIPE, stderr=STDOUT, check=False)
    if _.stdout and _.stdout.decode("utf-8").find("musl") != -1:
        return True
    return False


def is_library_installed(name: str) -> bool:
    if name.find("main") != -1 and name.find("reference") != -1:
        raise Exception("`name` param can not contain `main` and `reference` substrings.")
    _r = run(f"gcc -l{name}".split(), stdout=PIPE, stderr=STDOUT, check=False)
    if _r.stdout:
        _ = _r.stdout.decode("utf-8")
        if _.find("main") != -1 and _.find("reference") != -1:
            return True
    return False


def run_print_if_error(args) -> None:
    _ = run(args, stdout=PIPE, stderr=STDOUT, check=False)
    if _.returncode != 0:
        print(_.stdout.decode("utf-8"), flush=True)
        raise ChildProcessError(f"Failed: {args}")


def build_lib_linux(url: str, name: str, musl: bool = False):
    _lib_path = path.join(BUILD_DIR_LIBS, name)
    if path.isdir(_lib_path):
        print(f"Cache found for {name}", flush=True)
        chdir(path.join(_lib_path, "build")) if name != "x265" else chdir(_lib_path)
    else:
        _hide_build_process = True
        _script_dir = path.dirname(path.abspath(__file__))
        _linux_dir = path.join(_script_dir, "linux")
        if name == "x265":
            linux_build_tools.download_extract_to(url, _lib_path)
            chdir(_lib_path)
        else:
            _build_path = path.join(_lib_path, "build")
            makedirs(_build_path)
            if name == "aom":
                linux_build_tools.download_extract_to(url, path.join(_lib_path, "aom"), False)
                if musl:
                    patch_path = path.join(_linux_dir, "aom-musl/fix-stack-size-e53da0b-2.patch")
                    chdir(path.join(_lib_path, "aom"))
                    run(f"patch -p 1 -i {patch_path}".split(), check=True)
            else:
                linux_build_tools.download_extract_to(url, _lib_path)
                if name == "libde265":
                    chdir(_lib_path)
                    # for patch in (
                    #     "libde265/CVE-2022-1253.patch",
                    # ):
                    #     patch_path = path.join(_linux_dir, patch)
                    #     run(f"patch -p 1 -i {patch_path}".split(), check=True)
                elif name == "libheif":
                    chdir(_lib_path)
                    for patch in ("libheif/001-aom-remove-extend_padding_to_size.patch",):
                        patch_path = path.join(_linux_dir, patch)
                        run(f"patch -p 1 -i {patch_path}".split(), check=True)
            chdir(_build_path)
        print(f"Preconfiguring {name}...", flush=True)
        if name == "aom":
            cmake_args = "-DENABLE_TESTS=0 -DENABLE_TOOLS=0 -DENABLE_EXAMPLES=0 -DENABLE_DOCS=0".split()
            cmake_args += "-DENABLE_TESTDATA=0 -DCONFIG_AV1_ENCODER=1 -DCMAKE_BUILD_TYPE=Release".split()
            cmake_args += "-DCMAKE_INSTALL_LIBDIR=lib -DBUILD_SHARED_LIBS=1".split()
            cmake_args += f"-DCMAKE_INSTALL_PREFIX={INSTALL_DIR_LIBS} ../aom".split()
        elif name == "x265":
            cmake_high_bits = "-DHIGH_BIT_DEPTH=ON -DEXPORT_C_API=OFF".split()
            cmake_high_bits += "-DENABLE_SHARED=OFF -DENABLE_CLI=OFF".split()
            mkdir("12bit")
            mkdir("10bit")
            chdir("10bit")
            run("cmake ./../source -DENABLE_HDR10_PLUS=ON".split() + cmake_high_bits, check=True)
            run_print_if_error("make -j4".split())
            run("mv libx265.a ../libx265_main10.a".split(), check=True)
            chdir("../12bit")
            run(["cmake"] + ["./../source", "-DMAIN12=ON"] + cmake_high_bits, check=True)
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
                cmake_args += "-DWITH_EXAMPLES=OFF -DWITH_RAV1E=OFF -DWITH_DAV1D=OFF".split()
                _hide_build_process = False
                if musl:
                    cmake_args += [f"-DCMAKE_INSTALL_LIBDIR={INSTALL_DIR_LIBS}/lib"]
        run(["cmake"] + cmake_args, check=True)
        print(f"{name} configured. building...", flush=True)
        if _hide_build_process:
            run_print_if_error("make -j4".split())
        else:
            run("make -j4".split(), check=True)
        print(f"{name} build success.", flush=True)
    run("make install".split(), check=True)
    if musl:
        run(f"ldconfig {INSTALL_DIR_LIBS}/lib".split(), check=True)
    else:
        run("ldconfig", check=True)


def build_lib_linux_armv7(url: str, name: str, musl: bool = False):
    _lib_path = path.join(BUILD_DIR_LIBS, name)
    linux_build_tools.download_extract_to(url, _lib_path)
    chdir(_lib_path)
    if name == "libde265":
        run(["./autogen.sh"], check=True)
    print(f"Preconfiguring {name}...", flush=True)
    configure_args = f"--prefix {INSTALL_DIR_LIBS}".split()
    if name == "libde265":
        configure_args += "--disable-sherlock265 --disable-dec265 --disable-dependency-tracking".split()
    elif name == "libheif":
        configure_args += "--disable-examples --disable-go".split()
        configure_args += "--disable-gdk-pixbuf --disable-visibility".split()
    run(["./configure"] + configure_args, check=True)
    print(f"{name} configured. building...", flush=True)
    run("make -j4".split(), check=True)
    print(f"{name} build success.", flush=True)
    run("make install".split(), check=True)
    if musl:
        run(f"ldconfig {INSTALL_DIR_LIBS}/lib".split(), check=True)
    else:
        run("ldconfig", check=True)


def build_libs() -> str:
    _is_musllinux = is_musllinux()
    if is_library_installed("heif") or is_library_installed("libheif"):
        print("libheif is already present.")
        return INSTALL_DIR_LIBS
    _original_dir = getcwd()
    try:
        linux_build_tools.build_tools(_is_musllinux, machine().find("armv7") != -1)
        if not is_library_installed("x265"):
            if not PH_LIGHT_VERSION:
                build_lib_linux(
                    "https://bitbucket.org/multicoreware/x265_git/get/0b75c44c10e605fe9e9ebed58f04a46271131827.tar.gz",
                    "x265",
                    _is_musllinux,
                )
        else:
            print("x265 already installed.")
        if not is_library_installed("aom"):
            if not PH_LIGHT_VERSION:
                build_lib_linux("https://aomedia.googlesource.com/aom/+archive/v3.5.0.tar.gz", "aom", _is_musllinux)
        else:
            print("aom already installed.")
        if not is_library_installed("libde265") and not is_library_installed("de265"):
            if machine().find("armv7") == -1:
                build_lib_linux(
                    "https://github.com/strukturag/libde265/releases/download/v1.0.9/libde265-1.0.9.tar.gz",
                    "libde265",
                    _is_musllinux,
                )
            else:
                build_lib_linux_armv7(
                    "https://github.com/strukturag/libde265/releases/download/v1.0.9/libde265-1.0.9.tar.gz",
                    "libde265",
                    _is_musllinux,
                )
        else:
            print("libde265 already installed.")
        if machine().find("armv7") == -1:
            build_lib_linux(
                "https://github.com/strukturag/libheif/releases/download/v1.13.0/libheif-1.13.0.tar.gz",
                "libheif",
                _is_musllinux,
            )
        else:
            build_lib_linux_armv7(
                "https://github.com/strukturag/libheif/releases/download/v1.13.0/libheif-1.13.0.tar.gz",
                "libheif",
                _is_musllinux,
            )
    finally:
        chdir(_original_dir)
    return INSTALL_DIR_LIBS
