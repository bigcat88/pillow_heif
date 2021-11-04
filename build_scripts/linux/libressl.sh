VERSION="3.1.5"
NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
URL="https://github.com/libressl-portable/portable/archive/v$VERSION.tar.gz"
cd "/host/$BUILD_STUFF" || exit 2
if [[ -d "$NAME" ]]; then
  echo "Cache found for $NAME, install it..."
  cd "$NAME" || exit 102
else
  echo "No cache found for $NAME, build it..."
  mkdir "$NAME"
  wget -q --no-check-certificate -O "$NAME.tar.gz" "$URL" \
  && tar xf "$NAME.tar.gz" -C "$NAME" --strip-components 1 \
  && rm -f "$NAME.tar.gz" \
  && cd "$NAME" \
  && ./autogen.sh \
  && ./configure \
  && make -j4
fi
make install
# TEST VERSION2