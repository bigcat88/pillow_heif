NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
cd /host/build-deps || exit 2
if [[ -d "$NAME-$1" ]]; then
  echo "Cache found for $NAME, install it..."
  cd "$NAME-$1" || exit 102
else
  echo "No cache found for $NAME, build it..."
  wget -q "https://github.com/strukturag/libde265/releases/download/v$1/$NAME-$1.tar.gz" \
  && tar xf "$NAME-$1.tar.gz" \
  && rm -f "$NAME-$1.tar.gz" \
  && cd "$NAME-$1" \
  && ./autogen.sh \
  && ./configure --disable-sherlock265 --prefix /usr \
  && make -j4
fi
make install && ldconfig