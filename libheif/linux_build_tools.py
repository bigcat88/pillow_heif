from os import chdir, environ, makedirs, path, remove
from re import IGNORECASE, MULTILINE, search
from subprocess import DEVNULL, PIPE, CalledProcessError, TimeoutExpired, run

BUILD_DIR_PREFIX = environ.get("BUILD_DIR_PREFIX", "/tmp/pillow_heif")
BUILD_DIR_TOOLS = path.join(BUILD_DIR_PREFIX, "build-tools")


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
        raise EnvironmentError("Both curl and wget cannot be found.")
    return False


def download_extract_to(url: str, out_path: str, strip: bool = True):
    makedirs(out_path, exist_ok=True)
    _archive_path = path.join(out_path, "download.tar.gz")
    download_file(url, _archive_path)
    _tar_cmd = f"tar -xf {_archive_path} -C {out_path}"
    if strip:
        _tar_cmd += " --strip-components 1"
    run(_tar_cmd.split(), check=True)
    remove(_archive_path)


def build_tool(url: str, name: str, min_version: str, configure_args: list = None, chmod=None):
    if min_version:
        if tool_check_version(name, min_version):
            return
    if configure_args is None:
        configure_args = []
    _tool_path = path.join(BUILD_DIR_TOOLS, name)
    if path.isdir(_tool_path):
        print(f"Cache found for {name}", flush=True)
        chdir(_tool_path)
    else:
        download_extract_to(url, _tool_path)
        chdir(_tool_path)
        if name == "cmake":
            run("./bootstrap -- -DCMAKE_USE_OPENSSL=OFF".split(), check=True)
        else:
            run(["./configure"] + configure_args, check=True)
        run("make".split(), check=True)
    run("make install".split(), check=True)
    run(f"{name} --version".split(), check=True)
    if chmod:
        run(f"chmod -R {chmod} {_tool_path}".split(), check=True)


def tool_check_version(name: str, min_version: str) -> bool:
    try:
        _ = run([name, "--version"], stdout=PIPE, stderr=DEVNULL, check=True)
    except (CalledProcessError, FileNotFoundError):
        return False
    if name == "nasm":
        _regexp = r"version\s*(\d+(\.\d+){2})"
    elif name == "autoconf":
        _regexp = r"(\d+(\.\d+){1})$"
    else:
        _regexp = r"(\d+(\.\d+){2})$"
    m_groups = search(_regexp, _.stdout.decode("utf-8"), flags=MULTILINE + IGNORECASE)
    if m_groups is None:
        return False
    current_version = tuple(map(int, str(m_groups.groups()[0]).split(".")))
    min_version = tuple(map(int, min_version.split(".")))
    if current_version >= min_version:
        print(f"Tool {name} with version {str(m_groups.groups()[0])} satisfy requirements.", flush=True)
        return True
    return False


def build_tools(musl: bool, armv7: bool):
    if armv7:
        build_tool(
            "https://pkg-config.freedesktop.org/releases/pkg-config-0.29.2.tar.gz",
            "pkg-config",
            "0.29.1" if not musl else "",
            configure_args=["--with-internal-glib"],
        )
        build_tool("https://ftp.gnu.org/gnu/autoconf/autoconf-2.71.tar.gz", "autoconf", "2.69")
        build_tool("https://ftp.gnu.org/gnu/automake/automake-1.16.5.tar.gz", "automake", "1.16.1")
    build_tool("https://github.com/Kitware/CMake/archive/refs/tags/v3.22.3.tar.gz", "cmake", "3.16.1")
    nasm_url = "https://www.nasm.us/pub/nasm/releasebuilds/2.15.05/nasm-2.15.05.tar.gz"
    build_tool(nasm_url, "nasm", "2.15.05", chmod="774")
