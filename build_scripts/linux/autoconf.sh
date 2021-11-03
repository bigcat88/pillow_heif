NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
cd /host/build-tools || exit 2
if [[ -d "$NAME-$1" ]]; then
  echo "Cache found for $NAME, install it..."
  cd "$NAME-$1" || exit 102
else
  echo "No cache found for $NAME, build it..."
  wget -q --no-check-certificate "https://ftp.gnu.org/gnu/autoconf/$NAME-$1.tar.gz" \
  && tar xvf "$NAME-$1.tar.gz" \
  && cd "$NAME-$1" \
  && ./configure \
  && make -j4
fi
make install \
&& autoconf --version