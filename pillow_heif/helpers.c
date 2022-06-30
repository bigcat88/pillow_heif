#ifdef __cplusplus
    extern "C" {
#endif

void copy_image_data(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows)
{
    if (in_stride == out_stride)
        memcpy(out, in, out_stride * n_rows);
    else
        for (int i = 0; i < n_rows; i++)
            memcpy(out + out_stride * i, in + in_stride * i, out_stride);
}

void convert_i16_to_i10(const uint16_t *in, int in_stride, uint16_t *out, int out_stride, int n_rows, int stride_elements)
{
    uint16_t* in_row = in;
    uint16_t* out_row = out;
    for (int i = 0; i < n_rows; i++) {
        for (int i2 = 0; i2 < stride_elements; i2++)
            out_row[i2] = in_row[i2] >> 6;
        in_row += in_stride;
        out_row += out_stride;
    }
}

void convert_rgba_to_rgba16(const uint8_t *in, int in_stride, uint16_t *out, int out_stride, int n_rows, int stride_elements)
{
    uint8_t* in_row = in;
    uint16_t* out_row = out;
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

void convert_rgba_to_bgra16(const uint8_t *in, int in_stride, uint16_t *out, int out_stride, int n_rows, int stride_elements)
{
    uint8_t* in_row = in;
    uint16_t* out_row = out;
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

void convert_rgb_to_rgb16(const uint8_t *in, int in_stride, uint16_t *out, int out_stride, int n_rows, int stride_elements)
{
    uint8_t* in_row = in;
    uint16_t* out_row = out;
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

void convert_rgb_to_bgr16(const uint8_t *in, int in_stride, uint16_t *out, int out_stride, int n_rows, int stride_elements)
{
    uint8_t* in_row = in;
    uint16_t* out_row = out;
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

void convert_bgra_rgba(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows, int stride_elements)
{
    uint8_t* in_row = in;
    uint8_t* out_row = out;
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

void convert_bgr_rgb(const uint8_t *in, int in_stride, uint8_t *out, int out_stride, int n_rows, int stride_elements)
{
    uint8_t* in_row = in;
    uint8_t* out_row = out;
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

#ifdef __cplusplus
    }
#endif
