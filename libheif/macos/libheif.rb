# https://github.com/Homebrew/homebrew-core/blob/master/Formula/lib/libheif.rb

class Libheif < Formula
  desc "ISO/IEC 23008-12:2017 HEIF file format decoder and encoder"
  homepage "https://www.libde265.org/"
  url "https://github.com/strukturag/libheif/releases/download/v1.19.8/libheif-1.19.8.tar.gz"
  sha256 "6c4a5b08e6eae66d199977468859dea3b5e059081db8928f7c7c16e53836c906"
  license "LGPL-3.0-only"
  # Set current revision from what it was taken plus 10
  revision 10

  depends_on "cmake" => :build
  depends_on "pkgconf" => :build

  depends_on "jpeg-turbo"
  depends_on "libde265"
  depends_on "libpng"
  depends_on "libtiff"
  depends_on "shared-mime-info"
  depends_on "webp"
  depends_on "x265"

  def install
    args = %W[
      -DWITH_OPENJPH_DECODER=OFF
      -DWITH_OPENJPH_ENCODER=OFF
      -DWITH_HEADER_COMPRESSION=OFF
      -DWITH_LIBDE265=ON
      -DWITH_LIBDE265_PLUGIN=OFF
      -DWITH_X265=ON
      -DWITH_X265_PLUGIN=OFF
      -DWITH_AOM_DECODER=OFF
      -DWITH_AOM_DECODER_PLUGIN=OFF
      -DWITH_AOM_ENCODER=OFF
      -DWITH_AOM_ENCODER_PLUGIN=OFF
      -DWITH_RAV1E=OFF
      -DWITH_RAV1E_PLUGIN=OFF
      -DWITH_DAV1D=OFF
      -DWITH_DAV1D_PLUGIN=OFF
      -DWITH_SvtEnc=OFF
      -DWITH_SvtEnc_PLUGIN=OFF
      -DWITH_KVAZAAR=OFF
      -DWITH_KVAZAAR_PLUGIN=OFF
      -DWITH_FFMPEG_DECODER=OFF
      -DWITH_FFMPEG_DECODER_PLUGIN=OFF
      -DWITH_JPEG_DECODER=OFF
      -DWITH_JPEG_ENCODER=OFF
      -DWITH_OpenJPEG_DECODER=OFF
      -DWITH_OpenJPEG_ENCODER=OFF
      -DENABLE_PLUGIN_LOADING=OFF
      -DWITH_LIBSHARPYUV=OFF
      -DWITH_GDK_PIXBUF=OFF
      -DCMAKE_INSTALL_RPATH=#{rpath}
    ]

    system "cmake", "-S", ".", "-B", "build", *args, *std_cmake_args
    system "cmake", "--build", "build"
    system "cmake", "--install", "build"
    pkgshare.install "examples/example.heic"
  end

  def post_install
    system Formula["shared-mime-info"].opt_bin/"update-mime-database", "#{HOMEBREW_PREFIX}/share/mime"
  end

  test do
    output = "File contains 2 images"
    example = pkgshare/"example.heic"
    exout = testpath/"exampleheic.jpg"

    assert_match output, shell_output("#{bin}/heif-convert #{example} #{exout}")
    assert_path_exists testpath/"exampleheic-1.jpg"
    assert_path_exists testpath/"exampleheic-2.jpg"
  end
end
