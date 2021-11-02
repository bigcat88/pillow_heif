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