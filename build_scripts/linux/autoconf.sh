cd /host/build-tools || exit 2
ls -la
if [[ -d autoconf-"$1" ]]
then
  echo "No cache found for autoconf, build it..."
  wget --no-check-certificate https://ftp.gnu.org/gnu/autoconf/autoconf-"$1".tar.gz \
  && tar xvf autoconf-"$1".tar.gz \
  && cd autoconf-"$1" \
  && ./configure \
  && make -j4
else
  echo "Cache found for autoconf, install it..."
fi
make install \
&& autoconf --version