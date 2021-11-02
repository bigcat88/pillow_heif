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