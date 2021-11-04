VERSION="3.21.2"
NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
URL="https://github.com/Kitware/CMake/releases/download/v$VERSION/$NAME-$VERSION-linux-$(uname -m).sh"
cd "/host/$BUILD_STUFF" || exit 2
ls -la
if [[ -d "$NAME" ]]; then
  echo "Cache found for $NAME, install it..."
  cd "$NAME" || exit 102
else
  echo "No cache found for $NAME, download it..."
  mkdir "$NAME" && cd "$NAME" || exit 104
  wget -q -O "$NAME.sh" "$URL"
fi
chmod +x "$NAME.sh"
sh "$NAME.sh" --prefix=/usr/local/ --exclude-subdir
/usr/local/bin/cmake --version
# TEST VERSION11