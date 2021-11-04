VERSION="bb35ba9148543f22ba7d8642e4fbd29ae301f5dc"
NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
URL="https://aomedia.googlesource.com/aom/+archive/$VERSION.tar.gz"
cd "/host/$BUILD_STUFF" || exit 2
if [[ -d "$NAME" ]]; then
  echo "Cache found for lib$NAME, install it..."
  cd "$NAME/build" || exit 102
else
  echo "No cache found for lib$NAME, build it..."
  mkdir "$NAME" "$NAME/build" "$NAME/$NAME" && cd "$NAME" || exit 104
  wget -q --no-check-certificate -O "$NAME.tar.gz" "$URL" \
  && tar xf "$NAME.tar.gz" -C "$NAME" \
  && rm -f "$NAME.tar.gz" \
  && cd "./build" \
  && cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib -DBUILD_SHARED_LIBS=1 "../$NAME" \
  && make -j4
fi
make install && ldconfig