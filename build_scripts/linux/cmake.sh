os_architecture=$(uname -m)
cd /host/build-tools || exit 2
if [[ $os_architecture == "x86_64" ]]
then
  wget -q "https://github.com/Kitware/CMake/releases/download/v$1/cmake-$1-linux-x86_64.sh" \
  && chmod +x "cmake-$1-linux-x86_64.sh" \
  && sh "cmake-$1-linux-x86_64.sh" --prefix=/usr/local/ --exclude-subdir
elif [[ $os_architecture == "aarch64" ]]
then
  wget -q "https://github.com/Kitware/CMake/releases/download/v$1/cmake-$1-linux-aarch64.sh" \
  && chmod +x "cmake-$1-linux-aarch64.sh" \
  && sh "cmake-$1-linux-aarch64.sh" --prefix=/usr/local/ --exclude-subdir
else
  echo "$os_architecture"
  echo "Cant determine CPU architecture for CMAKE install!"
  exit 2
fi
/usr/local/bin/cmake --version