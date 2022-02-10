VERSION="v3.2.0"
NAME=$(basename "$0" | cut -f 1 -d '.')
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
  && MINIMAL_INSTALL="-DENABLE_TESTS=0 -DENABLE_TOOLS=0 -DENABLE_EXAMPLES=0 -DENABLE_DOCS=0" \
  && cmake "$MINIMAL_INSTALL" -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib -DBUILD_SHARED_LIBS=1 "../$NAME" \
  && make -j4
fi
if [[ -z "$LDCONFIG_ARG" ]]; then
  make install && ldconfig
else
  make install && ldconfig "$LDCONFIG_ARG"
fi
