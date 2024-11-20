# https://github.com/Homebrew/homebrew-core/blob/master/Formula/lib/libheif.rb

class Libheif < Formula
  desc "ISO/IEC 23008-12:2017 HEIF file format decoder and encoder"
  homepage "https://www.libde265.org/"
  url "https://github.com/strukturag/libheif/releases/download/v1.19.5/libheif-1.19.5.tar.gz"
  sha256 "d3cf0a76076115a070f9bc87cf5259b333a1f05806500045338798486d0afbaf"
  license "LGPL-3.0-only"
  # Set current revision from what it was taken plus 10
  revision 10

  depends_on "cmake" => :build
  depends_on "pkg-config" => :build

  depends_on "libde265"

  def install
    args = %W[
      -DWITH_OPENJPH_DECODER=OFF
      -DWITH_OPENJPH_ENCODER=OFF
      -DWITH_HEADER_COMPRESSION=OFF
      -DWITH_LIBDE265=ON
      -DWITH_LIBDE265_PLUGIN=OFF
      -DWITH_X265=OFF
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
      -DWITH_EXAMPLES=OFF
      -DCMAKE_INSTALL_RPATH=#{rpath}
    ]

    system "cmake", "-S", ".", "-B", "build", *args, *std_cmake_args
    system "cmake", "--build", "build"
    system "cmake", "--install", "build"
  end
end
