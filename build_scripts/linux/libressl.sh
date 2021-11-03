cd /host/build-deps || exit 2
if [[ -d "libressl-$1" ]]; then
  echo "Cache found for LibreSSL, install it..."
  cd "libressl-$1" || exit 102
else
  echo "No cache found for LibreSSL, build it..."
  wget -O "libressl-$1.tar.gz" "https://github.com/libressl-portable/portable/archive/v$1.tar.gz" \
  && tar xvf "libressl-$1.tar.gz" --one-top-level \
  && echo $(ls -la)
fi
make install