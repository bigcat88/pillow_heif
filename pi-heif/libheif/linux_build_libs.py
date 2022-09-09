from os import chdir, environ, getcwd, makedirs, path
from platform import machine
from subprocess import PIPE, STDOUT, run

from libheif import linux_build_tools

BUILD_DIR_PREFIX = environ.get("BUILD_DIR_PREFIX", "/tmp/pillow_heif")
BUILD_DIR_LIBS = path.join(BUILD_DIR_PREFIX, "build-stuff")
INSTALL_DIR_LIBS = environ.get("INSTALL_DIR_LIBS", "/usr")


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
        chdir(path.join(_lib_path, "build"))
    else:
        _hide_build_process = True
        _script_dir = path.dirname(path.abspath(__file__))
        _linux_dir = path.join(_script_dir, "linux")
        _build_path = path.join(_lib_path, "build")
        makedirs(_build_path)
        linux_build_tools.download_extract_to(url, _lib_path)
        chdir(_lib_path)
        if name == "libde265":
            for patch in (
                "libde265/CVE-2022-1253.patch",
                "libde265/CVE-2021-36408.patch",
                "libde265/CVE-2021-36410.patch",
                "libde265/CVE-2021-35452.patch",
                "libde265/CVE-2021-36411.patch",
            ):
                patch_path = path.join(_linux_dir, patch)
                run(f"patch -p 1 -i {patch_path}".split(), check=True)
        # elif name == "libheif":
        #     chdir(_lib_path)
        #     for patch in ():
        #         patch_path = path.join(_linux_dir, patch)
        #         run(f"patch -p 1 -i {patch_path}".split(), check=True)
        chdir(_build_path)
        print(f"Preconfiguring {name}...", flush=True)
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
        linux_build_tools.build_tools(_is_musllinux)
        if not is_library_installed("libde265") and not is_library_installed("de265"):
            if machine().find("armv7") == -1:
                build_lib_linux(
                    "https://github.com/strukturag/libde265/releases/download/v1.0.8/libde265-1.0.8.tar.gz",
                    "libde265",
                    _is_musllinux,
                )
            else:
                build_lib_linux_armv7(
                    "https://github.com/strukturag/libde265/releases/download/v1.0.8/libde265-1.0.8.tar.gz",
                    "libde265",
                    _is_musllinux,
                )
        else:
            print("libde265 already installed.")
        if machine().find("armv7") == -1:
            build_lib_linux(
                "https://github.com/strukturag/libheif/releases/download/v1.12.0/libheif-1.12.0.tar.gz",
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
