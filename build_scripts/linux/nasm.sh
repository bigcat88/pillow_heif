cd /host/build-tools || exit 2
if [[ -d "nasm-$1" ]]; then
  echo "Cache found for nasm, install it..."
  cd "nasm-$1" || exit 102
else
  echo "No cache found for nasm, build it..."
  wget -q --no-check-certificate "https://www.nasm.us/pub/nasm/releasebuilds/$1/nasm-$1.tar.gz" \
  && tar xvf "nasm-$1.tar.gz" \
  && cd "nasm-$1" \
  && ./configure \
  && make -j4
fi
make install \
&& nasm --version