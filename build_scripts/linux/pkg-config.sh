VERSION="0.29.2"
NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
URL="https://pkg-config.freedesktop.org/releases/$NAME-$VERSION.tar.gz"
cd /host/build-stuff || exit 2
if [[ -d "$NAME" ]]; then
  echo "Cache found for $NAME, install it..."
  cd "$NAME" || exit 102
else
  echo "No cache found for $NAME, build it..."
  wget -q --no-check-certificate -O "$NAME.tar.gz" "$URL" \
  && tar xf "$NAME-$1.tar.gz" \
  && rm -f "$NAME-$1.tar.gz" \
  && cd "$NAME" \
  && ./configure --with-internal-glib \
  && make -j4
fi
make install \
&& pkg-config --version