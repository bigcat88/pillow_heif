#set -ex \
#    && cd /build-deps \
#    && LIBHEIF_VERSION="1.12.0" \
#    && wget https://github.com/strukturag/libheif/releases/download/v${LIBHEIF_VERSION}/libheif-${LIBHEIF_VERSION}.tar.gz \
#    && tar xvf libheif-${LIBHEIF_VERSION}.tar.gz \
#    && cd libheif-${LIBHEIF_VERSION} \
#    && ./configure --prefix /usr \
#    && make -j4 \
#    && make install \
#    && ldconfig