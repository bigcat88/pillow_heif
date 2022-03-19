export CIBW_SKIP="pp* cp36-* cp37-* cp38-*"
export CIBW_BUILD="*-macosx_arm64"
export CIBW_ARCHS=arm64
export CIBW_PLATFORM=macos
export CIBW_ENVIRONMENT="MACOSX_DEPLOYMENT_TARGET=12.0"

/opt/homebrew/Cellar/python@3.9/3.9.10/bin/python3 -m pip install --upgrade cibuildwheel
/opt/homebrew/Cellar/python@3.9/3.9.10/bin/python3 -m cibuildwheel --platform macos
