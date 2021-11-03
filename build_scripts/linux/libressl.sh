cd /host/build-deps || exit 2
if [[ -d "libressl-$1" ]]; then
  echo "Cache found for LibreSSL, install it..."
  cd "libressl-$1" || exit 102
else
  echo "No cache found for LibreSSL, build it..."
  mkdir "libressl-$1"
  wget "https://github.com/libressl-portable/portable/archive/v$1.tar.gz" \
  && ls -la \
  && tar xvf "v$1.tar.gz" -C "libressl-$1" --strip-components 1 \
  && ls -la "libressl-$1" \
  && cd "libressl-$1" \
  && ./autogen.sh \
  && ./configure \
  && make -j4
fi
make install