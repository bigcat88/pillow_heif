cd /host/build-deps || exit 2
if [[ -d "libffi-$1" ]]; then
  echo "Cache found for libffi, install it..."
  cd "libffi-$1" || exit 102
else
  echo "No cache found for libffi, build it..."
  wget -q --no-check-certificate "ftp://sourceware.org/pub/libffi/libffi-$1.tar.gz" \
  && tar xvf "libffi-$1.tar.gz" \
  && cd "libffi-$1" \
  && ./configure --prefix /usr \
  && make -j4
fi
make install && ldconfig