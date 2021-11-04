#          VERSION: "3.21.2"
NAME=$(basename "$BASH_SOURCE" | cut -f 1 -d '.')
os_architecture=$(uname -m)
cd /host/build-stuff || exit 2
if [[ $os_architecture == "x86_64" ]]
then
  wget -q "https://github.com/Kitware/CMake/releases/download/v$1/$NAME-$1-linux-x86_64.sh" \
  && chmod +x "$NAME-$1-linux-x86_64.sh" \
  && sh "$NAME-$1-linux-x86_64.sh" --prefix=/usr/local/ --exclude-subdir
elif [[ $os_architecture == "aarch64" ]]
then
  wget -q "https://github.com/Kitware/CMake/releases/download/v$1/$NAME-$1-linux-aarch64.sh" \
  && chmod +x "$NAME-$1-linux-aarch64.sh" \
  && sh "$NAME-$1-linux-aarch64.sh" --prefix=/usr/local/ --exclude-subdir
else
  echo "$os_architecture"
  echo "Cant determine CPU architecture for CMAKE install!"
  exit 2
fi
/usr/local/bin/cmake --version