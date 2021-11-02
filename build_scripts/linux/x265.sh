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