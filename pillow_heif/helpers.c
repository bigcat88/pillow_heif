#ifdef __cplusplus
    extern "C" {
#endif

void copy_image_data(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    if (in_stride == out_stride)
        memcpy(out, in, out_stride * n_rows);
    else
    {
        int stride_elements = out_stride > in_stride ? in_stride : out_stride;
        for (int i = 0; i < n_rows; i++)
            memcpy(out + out_stride * i, in + in_stride * i, stride_elements);
    }
}

void convert_i16_to_i10(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++)
            out_row[i2] = in_row[i2] >> 6;
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_i16_to_i12(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++)
            out_row[i2] = in_row[i2] >> 4;
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_bgr16_to_rgb10(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 3;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 3 + 0] = in_row[i2 * 3 + 2] >> 6;
            out_row[i2 * 3 + 1] = in_row[i2 * 3 + 1] >> 6;
            out_row[i2 * 3 + 2] = in_row[i2 * 3 + 0] >> 6;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_bgra16_to_rgba10(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 4;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 4 + 0] = in_row[i2 * 4 + 2] >> 6;
            out_row[i2 * 4 + 1] = in_row[i2 * 4 + 1] >> 6;
            out_row[i2 * 4 + 2] = in_row[i2 * 4 + 0] >> 6;
            out_row[i2 * 4 + 3] = in_row[i2 * 4 + 3] >> 6;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgb16_to_rgb10(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 3;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 3 + 0] = in_row[i2 * 3 + 0] >> 6;
            out_row[i2 * 3 + 1] = in_row[i2 * 3 + 1] >> 6;
            out_row[i2 * 3 + 2] = in_row[i2 * 3 + 2] >> 6;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgba16_to_rgba10(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 4;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 4 + 0] = in_row[i2 * 4 + 0] >> 6;
            out_row[i2 * 4 + 1] = in_row[i2 * 4 + 1] >> 6;
            out_row[i2 * 4 + 2] = in_row[i2 * 4 + 2] >> 6;
            out_row[i2 * 4 + 3] = in_row[i2 * 4 + 3] >> 6;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_bgr16_to_rgb12(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 3;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 3 + 0] = in_row[i2 * 3 + 2] >> 4;
            out_row[i2 * 3 + 1] = in_row[i2 * 3 + 1] >> 4;
            out_row[i2 * 3 + 2] = in_row[i2 * 3 + 0] >> 4;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_bgra16_to_rgba12(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 4;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 4 + 0] = in_row[i2 * 4 + 2] >> 4;
            out_row[i2 * 4 + 1] = in_row[i2 * 4 + 1] >> 4;
            out_row[i2 * 4 + 2] = in_row[i2 * 4 + 0] >> 4;
            out_row[i2 * 4 + 3] = in_row[i2 * 4 + 3] >> 4;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgb16_to_rgb12(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 3;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 3 + 0] = in_row[i2 * 3 + 0] >> 4;
            out_row[i2 * 3 + 1] = in_row[i2 * 3 + 1] >> 4;
            out_row[i2 * 3 + 2] = in_row[i2 * 3 + 2] >> 4;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgba16_to_rgba12(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 4;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 4 + 0] = in_row[i2 * 4 + 0] >> 4;
            out_row[i2 * 4 + 1] = in_row[i2 * 4 + 1] >> 4;
            out_row[i2 * 4 + 2] = in_row[i2 * 4 + 2] >> 4;
            out_row[i2 * 4 + 3] = in_row[i2 * 4 + 3] >> 4;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgba16_to_rgba(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint8_t* out_row = out;
    in_stride = in_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 4;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 4 + 0] = in_row[i2 * 4 + 0] >> 8;
            out_row[i2 * 4 + 1] = in_row[i2 * 4 + 1] >> 8;
            out_row[i2 * 4 + 2] = in_row[i2 * 4 + 2] >> 8;
            out_row[i2 * 4 + 3] = in_row[i2 * 4 + 3] >> 8;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgba12_to_rgba16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 4;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 4 + 0] = in_row[i2 * 4 + 0] << 4;
            out_row[i2 * 4 + 1] = in_row[i2 * 4 + 1] << 4;
            out_row[i2 * 4 + 2] = in_row[i2 * 4 + 2] << 4;
            out_row[i2 * 4 + 3] = in_row[i2 * 4 + 3] << 4;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgba12_to_bgra16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 4;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 4 + 0] = in_row[i2 * 4 + 2] << 4;
            out_row[i2 * 4 + 1] = in_row[i2 * 4 + 1] << 4;
            out_row[i2 * 4 + 2] = in_row[i2 * 4 + 0] << 4;
            out_row[i2 * 4 + 3] = in_row[i2 * 4 + 3] << 4;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgb12_to_rgb16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 3;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 3 + 0] = in_row[i2 * 3 + 0] << 4;
            out_row[i2 * 3 + 1] = in_row[i2 * 3 + 1] << 4;
            out_row[i2 * 3 + 2] = in_row[i2 * 3 + 2] << 4;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgb12_to_bgr16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 3;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 3 + 0] = in_row[i2 * 3 + 2] << 4;
            out_row[i2 * 3 + 1] = in_row[i2 * 3 + 1] << 4;
            out_row[i2 * 3 + 2] = in_row[i2 * 3 + 0] << 4;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgba10_to_rgba16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 4;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 4 + 0] = in_row[i2 * 4 + 0] << 6;
            out_row[i2 * 4 + 1] = in_row[i2 * 4 + 1] << 6;
            out_row[i2 * 4 + 2] = in_row[i2 * 4 + 2] << 6;
            out_row[i2 * 4 + 3] = in_row[i2 * 4 + 3] << 6;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgba10_to_bgra16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 4;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 4 + 0] = in_row[i2 * 4 + 2] << 6;
            out_row[i2 * 4 + 1] = in_row[i2 * 4 + 1] << 6;
            out_row[i2 * 4 + 2] = in_row[i2 * 4 + 0] << 6;
            out_row[i2 * 4 + 3] = in_row[i2 * 4 + 3] << 6;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgb10_to_rgb16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 3;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 3 + 0] = in_row[i2 * 3 + 0] << 6;
            out_row[i2 * 3 + 1] = in_row[i2 * 3 + 1] << 6;
            out_row[i2 * 3 + 2] = in_row[i2 * 3 + 2] << 6;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgb10_to_bgr16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint16_t* in_row = (uint16_t*)in;
    uint16_t* out_row = (uint16_t*)out;
    in_stride = in_stride / 2;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 3;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 3 + 0] = in_row[i2 * 3 + 2] << 6;
            out_row[i2 * 3 + 1] = in_row[i2 * 3 + 1] << 6;
            out_row[i2 * 3 + 2] = in_row[i2 * 3 + 0] << 6;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgba_to_rgba16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint8_t* in_row = in;
    uint16_t* out_row = (uint16_t*)out;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 4;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 4 + 0] = in_row[i2 * 4 + 0] << 8;
            out_row[i2 * 4 + 1] = in_row[i2 * 4 + 1] << 8;
            out_row[i2 * 4 + 2] = in_row[i2 * 4 + 2] << 8;
            out_row[i2 * 4 + 3] = in_row[i2 * 4 + 3] << 8;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgba_to_bgra16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint8_t* in_row = in;
    uint16_t* out_row = (uint16_t*)out;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 4;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 4 + 0] = in_row[i2 * 4 + 2] << 8;
            out_row[i2 * 4 + 1] = in_row[i2 * 4 + 1] << 8;
            out_row[i2 * 4 + 2] = in_row[i2 * 4 + 0] << 8;
            out_row[i2 * 4 + 3] = in_row[i2 * 4 + 3] << 8;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgb_to_rgb16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint8_t* in_row = in;
    uint16_t* out_row = (uint16_t*)out;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 3;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 3 + 0] = in_row[i2 * 3 + 0] << 8;
            out_row[i2 * 3 + 1] = in_row[i2 * 3 + 1] << 8;
            out_row[i2 * 3 + 2] = in_row[i2 * 3 + 2] << 8;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgb_to_bgr16(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint8_t* in_row = in;
    uint16_t* out_row = (uint16_t*)out;
    out_stride = out_stride / 2;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 3;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 3 + 0] = in_row[i2 * 3 + 2] << 8;
            out_row[i2 * 3 + 1] = in_row[i2 * 3 + 1] << 8;
            out_row[i2 * 3 + 2] = in_row[i2 * 3 + 0] << 8;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_bgra_rgba(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint8_t* in_row = in;
    uint8_t* out_row = out;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 4;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 4 + 0] = in_row[i2 * 4 + 2];
            out_row[i2 * 4 + 1] = in_row[i2 * 4 + 1];
            out_row[i2 * 4 + 2] = in_row[i2 * 4 + 0];
            out_row[i2 * 4 + 3] = in_row[i2 * 4 + 3];
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_bgr_rgb(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint8_t* in_row = in;
    uint8_t* out_row = out;
    int stride_elements = out_stride > in_stride ? in_stride : out_stride;
    stride_elements = stride_elements / 3;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            out_row[i2 * 3 + 0] = in_row[i2 * 3 + 2];
            out_row[i2 * 3 + 1] = in_row[i2 * 3 + 1];
            out_row[i2 * 3 + 2] = in_row[i2 * 3 + 0];
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgba_premultiplied_to_rgb(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint32_t* in_row = (uint32_t*)in;
    uint8_t* out_row = out;
    in_stride = in_stride / 4;
    int stride_elements = out_stride / 3 > in_stride ? in_stride : out_stride / 3;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            uint32_t p = in_row[i2];
            uint8_t a =  (p >> 24) & 0xFF;
            out_row[i2 * 3 + 0] = (((p >> 0) & 0xFF) * a) / 255;
            out_row[i2 * 3 + 1] = (((p >> 8) & 0xFF) * a) / 255;
            out_row[i2 * 3 + 2] = (((p >> 16) & 0xFF) * a) / 255;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgba_premultiplied_to_bgr(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    const uint32_t* in_row = (uint32_t*)in;
    uint8_t* out_row = out;
    in_stride = in_stride / 4;
    int stride_elements = out_stride / 3 > in_stride ? in_stride : out_stride / 3;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++) {
            uint32_t p = in_row[i2];
            uint8_t a =  (p >> 24) & 0xFF;
            out_row[i2 * 3 + 0] = (((p >> 16) & 0xFF) * a) / 255;
            out_row[i2 * 3 + 1] = (((p >> 8) & 0xFF) * a) / 255;
            out_row[i2 * 3 + 2] = (((p >> 0) & 0xFF) * a) / 255;
        }
        in_row += in_stride;
        out_row += out_stride;
    }
}

#ifdef __cplusplus
    }
#endif
