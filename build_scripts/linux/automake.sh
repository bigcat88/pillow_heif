cd /host/build-tools || exit 2
if [[ -d "automake-$1" ]]; then
  echo "Cache found for automake, install it..."
  cd "automake-$1" || exit 102
else
  echo "No cache found for automake, build it..."
  wget -q --no-check-certificate "https://ftp.gnu.org/gnu/autoconf/automake-$1.tar.gz" \
  && tar xvf "automake-$1.tar.gz" \
  && cd "automake-$1" \
  && ./configure \
  && make -j4
fi
make install \
&& automake --version