VERSION="2.15.05"
NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
URL="https://www.nasm.us/pub/nasm/releasebuilds/$VERSION/$NAME-$VERSION.tar.gz"
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
  && ./configure \
  && make -j4
fi
make install \
&& nasm --version
# TEST VERSION1125