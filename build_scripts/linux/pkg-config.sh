VERSION="0.29.2"
NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
URL="https://pkg-config.freedesktop.org/releases/$NAME-$VERSION.tar.gz"
ls -la
cd "/host/$BUILD_STUFF" || exit 2
ls -la
exit 222
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
  && ./configure --with-internal-glib \
  && make -j4
fi
make install \
&& pkg-config --version
# TEST VERSION