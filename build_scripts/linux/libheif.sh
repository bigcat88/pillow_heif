VERSION="1.12.0"
NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
URL="https://github.com/strukturag/libheif/releases/download/v$VERSION/$NAME-$VERSION.tar.gz"
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
  && ./configure --prefix /usr \
  && make -j4
fi
make install && ldconfig
# TEST VERSION2