VERSION="bb35ba9148543f22ba7d8642e4fbd29ae301f5dc"
NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
URL="https://aomedia.googlesource.com/aom/+archive/$VERSION.tar.gz"
cd "/host/$BUILD_STUFF" || exit 2
if [[ -d "$NAME-build-$1" ]]; then
  echo "Cache found for lib$NAME, install it..."
  cd "$NAME-build-$1" || exit 102
else
  echo "No cache found for lib$NAME, build it..."
  mkdir "$NAME-build-$1" "$NAME-$1" && cd "$NAME-$1" || exit 104
  wget -q --no-check-certificate -O "$NAME.tar.gz" "$URL" \
  && tar xf "$NAME-$1.tar.gz" \
  && rm -f "$NAME-$1.tar.gz" \
  && cd "../$NAME-build-$1" \
  && cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib -DBUILD_SHARED_LIBS=1 "../$NAME-$1" \
  && make -j4
fi
make install && ldconfig
# TEST VERSION


VERSION="bb35ba9148543f22ba7d8642e4fbd29ae301f5dc"
NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
URL="https://aomedia.googlesource.com/aom/+archive/$VERSION.tar.gz"
cd "/host/$BUILD_STUFF" || exit 2
if [[ -d "$NAME-build-$1" ]]; then
  echo "Cache found for lib$NAME, install it..."
  cd "$NAME-build-$1" || exit 102
else
  echo "No cache found for lib$NAME, build it..."
  mkdir "$NAME-build-$1" "$NAME-$1" && cd "$NAME-$1" || exit 104
  wget -q --no-check-certificate -O "$NAME.tar.gz" "$URL" \
  && tar xf "$NAME-$1.tar.gz" \
  && rm -f "$NAME-$1.tar.gz" \
  && cd "../$NAME-build-$1" \
  && cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib -DBUILD_SHARED_LIBS=1 "../$NAME-$1" \
  && make -j4
fi
make install && ldconfig
# TEST VERSION