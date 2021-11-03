cd /host/build-deps || exit 2
if [[ -d "libde265-$1" ]]; then
  echo "Cache found for libde265, install it..."
  cd "libde265-$1" || exit 102
else
  echo "No cache found for libde265, build it..."
  wget -q "https://github.com/strukturag/libde265/releases/download/v$1/libde265-$1.tar.gz" \
  && tar xvf "libde265-$1.tar.gz" \
  && cd "libde265-$1" \
  && ./autogen.sh \
  && ./configure --disable-sherlock265 --prefix /usr \
  && make -j4
fi
make install && ldconfig