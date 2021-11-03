NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
cd /host/build-deps || exit 2
if [[ -d "$NAME-build-$1" ]]; then
  echo "Cache found for lib$NAME, install it..."
  cd "$NAME-build-$1" || exit 102
else
  echo "No cache found for lib$NAME, build it..."
  mkdir "$NAME-build-$1" "$NAME-$1" && cd "$NAME-$1" || exit 104
  wget -q --no-check-certificate -O "$NAME-$1.tar.gz" "https://aomedia.googlesource.com/aom/+archive/$1.tar.gz" \
  && ls -la \
  && tar xvf "$NAME-$1.tar.gz" \
  && ls -la \
  && cd "../$NAME-build-$1" \
  && ls -la \
  && cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib -DBUILD_SHARED_LIBS=1 "../$NAME-$1" \
  && ls -la \
  && make -j4 \
  && ls -la
fi
make install && ldconfig



#    && cd /build-deps \
#    && LIBAOM_COMMIT="bb35ba9148543f22ba7d8642e4fbd29ae301f5dc" \
#    && mkdir -v aom && mkdir -v aom_build && cd aom \
#    && wget "https://aomedia.googlesource.com/aom/+archive/${LIBAOM_COMMIT}.tar.gz" \
#    && tar xvf ${LIBAOM_COMMIT}.tar.gz \
#    && cd ../aom_build \
#    && cmake -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib -DBUILD_SHARED_LIBS=1 ../aom \
#    && make -j4 \
#    && make install \
#    && ldconfig