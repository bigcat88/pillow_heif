cd /host/build-deps || exit 2
if [[ -d "x265-$1" ]]; then
  echo "Cache found for x265, install it..."
  cd "x265-$1" || exit 102
else
  echo "No cache found for x265, build it..."
  mkdir "x265-$1"
  wget -O "x265-$1.tar.gz" "https://github.com/libressl-portable/portable/archive/v$1.tar.gz" \
  && tar xvf "x265-$1.tar.gz" -C "x265-$1" --strip-components 1 \
  && cd "x265-$1" \
  && cmake -DCMAKE_INSTALL_PREFIX=/usr -G "Unix Makefiles" ./source \
  && make -j4
fi
make install && ldconfig