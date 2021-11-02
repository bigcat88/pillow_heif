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