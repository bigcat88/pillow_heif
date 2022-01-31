VERSION="3.5"
NAME=$(basename "$0" | cut -f 1 -d '.')
URL="https://bitbucket.org/multicoreware/x265_git/get/$VERSION.tar.gz"
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
  && cmake -DCMAKE_INSTALL_PREFIX=/usr -G "Unix Makefiles" ./source \
  && make -j4
fi
make install && ldconfig