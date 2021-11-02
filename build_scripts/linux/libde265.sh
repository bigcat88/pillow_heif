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