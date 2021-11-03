NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
cd /host/build-deps || exit 2
if [[ -d "$NAME-$1" ]]; then
  echo "Cache found for $NAME, install it..."
  cd "$NAME-$1" || exit 102
else
  echo "No cache found for $NAME, build it..."
  mkdir "$NAME-$1"
  wget -q -O "$NAME-$1.tar.gz" "https://github.com/libressl-portable/portable/archive/v$1.tar.gz" \
  && tar xf "$NAME-$1.tar.gz" -C "$NAME-$1" --strip-components 1 \
  && rm -f "$NAME-$1.tar.gz" \
  && cd "$NAME-$1" \
  && ./autogen.sh \
  && ./configure \
  && make -j4
fi
make install