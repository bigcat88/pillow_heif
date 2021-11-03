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


    cd /host/build-deps || exit 2
if [[ -d "libressl-$1" ]]; then
  echo "Cache found for LibreSSL, install it..."
  cd "libressl-$1" || exit 102
else
  echo "No cache found for LibreSSL, build it..."
  wget -q "https://github.com/libressl-portable/portable/archive/v$1.tar.gz" \
  && tar xvf "portable-$1.tar.gz" \
  && echo $(ls -la) \
  && mv "portable-$1" "libressl-$1" \
  && echo $(ls -la) \
  && cd "libressl-$1" \
  && ./autogen.sh \
  && ./configure \
  && make -j4
fi
make install