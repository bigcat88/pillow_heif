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