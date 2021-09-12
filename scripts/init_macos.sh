set -ex \
    && /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

set -ex \
    && brew install libffi libheif

if [[ -z "${HOMEBREW_PREFIX}" ]]; then
  HOMEBREW_PREFIX=$(brew --prefix)
fi
