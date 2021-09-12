set -ex && mkdir /build-tools && mkdir /build-deps

set -ex \
    && cd /build-tools \
    && PKG_CONFIG_VERSION="0.29.2" \
    && wget https://pkg-config.freedesktop.org/releases/pkg-config-${PKG_CONFIG_VERSION}.tar.gz \
    && tar xvf pkg-config-${PKG_CONFIG_VERSION}.tar.gz \
    && cd pkg-config-${PKG_CONFIG_VERSION} \
    && ./configure --with-internal-glib \
    && make -j4 \
    && make install \
    && pkg-config --version

set -ex \
    && cd /build-tools \
    && CMAKE_VERSION="3.21.2" \
    && wget https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz \
    && tar xvf cmake-${CMAKE_VERSION}.tar.gz \
    && cd cmake-${CMAKE_VERSION} \
    && ./configure \
    && gmake -j4 \
    && make install \
    && cmake --version

set -ex \
    && cd /build-tools \
    && AUTOCONF_VERSION="2.71" \
    && wget https://ftp.gnu.org/gnu/autoconf/autoconf-${AUTOCONF_VERSION}.tar.gz \
    && tar xvf autoconf-${AUTOCONF_VERSION}.tar.gz \
    && cd autoconf-${AUTOCONF_VERSION} \
    && ./configure \
    && make -j4 \
    && make install \
    && autoconf --version

set -ex \
    && cd /build-tools \
    && AUTOMAKE_VERSION="1.16.4" \
    && wget https://ftp.gnu.org/gnu/automake/automake-${AUTOMAKE_VERSION}.tar.gz \
    && tar xvf automake-${AUTOMAKE_VERSION}.tar.gz \
    && cd automake-${AUTOMAKE_VERSION} \
    && ./configure \
    && make -j4 \
    && make install \
    && automake --version

set -ex \
    && cd /build-tools \
    && LIBRESSL_VERSION="3.1.5" \
    && wget https://github.com/libressl-portable/portable/archive/v${LIBRESSL_VERSION}.tar.gz \
    && tar xvf v${LIBRESSL_VERSION}.tar.gz \
    && cd portable-${LIBRESSL_VERSION} \
    && ./autogen.sh \
    && ./configure \
    && make -j4 \
    && make install

set -ex \
    && cd /build-tools \
    && NASM_VERSION="2.15.05" \
    && wget https://www.nasm.us/pub/nasm/releasebuilds/${NASM_VERSION}/nasm-${NASM_VERSION}.tar.gz \
    && tar xvf nasm-${NASM_VERSION}.tar.gz \
    && cd nasm-${NASM_VERSION} \
    && ./configure \
    && make -j4 \
    && make install \
    && nasm --version

set -ex \
    && cd /build-deps \
    && mkdir x265 \
    && X265_VERSION="3.5" \
    && wget -O ${X265_VERSION}.tar.gz https://bitbucket.org/multicoreware/x265_git/get/${X265_VERSION}.tar.gz \
    && tar xvf ${X265_VERSION}.tar.gz -C x265 --strip-components 1 \
    && cd x265 \
    && cmake -DCMAKE_INSTALL_PREFIX=/usr -G "Unix Makefiles" ./source \
    && make -j4 \
    && make install \
    && ldconfig

set -ex \
    && cd /build-deps \
    && LIBDE265_VERSION="1.0.8" \
    && wget https://github.com/strukturag/libde265/releases/download/v${LIBDE265_VERSION}/libde265-${LIBDE265_VERSION}.tar.gz \
    && tar xvf libde265-${LIBDE265_VERSION}.tar.gz \
    && cd libde265-${LIBDE265_VERSION} \
    && ./autogen.sh \
    && ./configure --disable-dec265 --disable-sherlock265 --prefix /usr \
    && make -j4 \
    && make install \
    && ldconfig

#set -ex \
#    && cd /build-deps \
#    && LIBAOM_COMMIT="bb35ba9148543f22ba7d8642e4fbd29ae301f5dc" \
#    && mkdir -v aom && mkdir -v aom_build && cd aom \
#    && wget "https://aomedia.googlesource.com/aom/+archive/${LIBAOM_COMMIT}.tar.gz" \
#    && tar xvf ${LIBAOM_COMMIT}.tar.gz \
#    && cd ../aom_build \
#    && cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib -DBUILD_SHARED_LIBS=1 ../aom \
#    && make -j4 \
#    && make install \
#    && ldconfig

set -ex \
    && cd /build-deps \
    && LIBHEIF_VERSION="1.12.0" \
    && wget https://github.com/strukturag/libheif/releases/download/v${LIBHEIF_VERSION}/libheif-${LIBHEIF_VERSION}.tar.gz \
    && tar xvf libheif-${LIBHEIF_VERSION}.tar.gz \
    && cd libheif-${LIBHEIF_VERSION} \
    && ./configure --prefix /usr \
    && make -j4 \
    && make install \
    && ldconfig

set -ex \
    && cd /build-deps \
    && LIBFFI_VERSION="3.3" \
    && wget ftp://sourceware.org/pub/libffi/libffi-${LIBFFI_VERSION}.tar.gz \
    && tar xvf libffi-${LIBFFI_VERSION}.tar.gz \
    && cd libffi-${LIBFFI_VERSION} \
    && ./configure --prefix /usr \
    && make -j4 \
    && make install \
    && ldconfig
