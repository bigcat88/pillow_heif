cd /host/build-tools || exit 2
ls -la
if [[ -d automake-"$1" ]]
then
  echo "No cache found for automake, build it..."
  wget --no-check-certificate https://ftp.gnu.org/gnu/autoconf/automake-"$1".tar.gz \
  && tar xvf automake-"$1".tar.gz \
  && cd automake-"$1" \
  && ./configure \
  && make -j4
else
  echo "Cache found for automake, install it..."
fi
make install \
&& automake --version