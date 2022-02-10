export CIBW_SKIP="pp* cp36-* cp37-* cp38-*"
export CIBW_TEST_COMMAND="pytest {project}"
export CIBW_TEST_REQUIRES="pytest piexif"
export CIBW_BUILD_VERBOSITY=2
export CIBW_BUILD="*-macosx_arm64"
export CIBW_ARCHS=arm64
export CIBW_PLATFORM=macos
export CIBW_ENVIRONMENT="MACOSX_DEPLOYMENT_TARGET=12.0"


cibuildwheel --platform macos
