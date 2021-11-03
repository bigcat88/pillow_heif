cd /host/build-deps || exit 2
if [[ -d "libressl-$1" ]]; then
  echo "Cache found for LibreSSL, install it..."
  cd "libressl-$1" || exit 102
else
  echo "No cache found for LibreSSL, build it..."
  wget "https://github.com/libressl-portable/portable/archive/v$1.tar.gz" \
  && tar xvf "v$1.tar.gz" \
  && mv "portable-$1" "libressl-$1" \
  && cd "libressl-$1" \
  && ./autogen.sh \
  && ./configure \
  && make -j4
fi
make install