#define PY_SSIZE_T_CLEAN

#include "Python.h"
#include "libheif/heif.h"

/* =========== Common stuff ======== */

#define RETURN_NONE Py_INCREF(Py_None); return Py_None;

static struct heif_error heif_error_no = { .code = 0, .subcode = 0, .message = NULL };

int check_error(struct heif_error error) {
    if (error.code == heif_error_Ok) {
        return 0;
    }

    PyObject* e;
    switch (error.code) {
        case heif_error_Decoder_plugin_error:
            if (error.subcode == 100) {
                e = PyExc_EOFError;
                break;
            }
        case heif_error_Invalid_input:
        case heif_error_Usage_error:
            e = PyExc_ValueError;
            break;
        case heif_error_Unsupported_filetype:
        case heif_error_Unsupported_feature:
        case heif_error_Color_profile_does_not_exist:
            e = PyExc_SyntaxError;
            break;
        default:
            e = PyExc_RuntimeError;
    }
    PyErr_SetString(e, error.message);
    return 1;
}

int __PyDict_SetItemString(PyObject *p, const char *key, PyObject *val) {
    int r = PyDict_SetItemString(p, key, val);
    Py_DECREF(val);
    return r;
}

/* =========== Objects ======== */

typedef struct {
    PyObject_HEAD
    enum heif_chroma chroma;
    struct heif_image* image;
    struct heif_image_handle* handle;
} CtxWriteImageObject;

static PyTypeObject CtxWriteImage_Type;

typedef struct {
    PyObject_HEAD
    struct heif_context* ctx;               // libheif context
    struct heif_encoder* encoder;           // encoder
    size_t size;                            // number of bytes in `data`
    void* data;                             // encoded data if success
} CtxWriteObject;

static PyTypeObject CtxWrite_Type;

typedef struct {
    PyObject_HEAD
    int width;                              // size[0];
    int height;                             // size[1];
    int bits;                               // on of: 8, 10, 12.
    int alpha;                              // on of: 0, 1.
    char mode[8];                           // one of: RGB, RGBA, RGBa, RGB;16, RGBA;16, RGBa;16
    int primary;                            // on of: 0, 1.
    int hdr_to_8bit;                        // private. decode option.
    int bgr_mode;                           // private. decode option.
    int postprocess;                        // private. decode option.
    int reload_size;                        // private. decode option.
    struct heif_image_handle *handle;       // private
    struct heif_image *heif_image;          // private
    uint8_t *data;                          // pointer to data after decoding
    int stride;                             // time when it get filled depends on `postprocess` value
    PyObject *file_bytes;                   // private
} CtxImageObject;

static PyTypeObject CtxImage_Type;

/* =========== CtxWriteImage ======== */

static void _CtxWriteImage_destructor(CtxWriteImageObject* self) {
    if (self->handle)
        heif_image_handle_release(self->handle);
    if (self->image)
        heif_image_release(self->image);
    PyObject_Del(self);
}

static PyObject* _CtxWriteImage_add_plane(CtxWriteImageObject* self, PyObject* args) {
    /* (size), depth: int, depth_in: int, data: bytes, bgr_mode: int */
    int width, height, depth, depth_in, stride, stride_in, bgr_mode;
    Py_buffer buffer;
    uint8_t* plane_data;

    if (!PyArg_ParseTuple(args, "(ii)iiy*i", &width, &height, &depth, &depth_in, &buffer, &bgr_mode))
        return NULL;

    int with_alpha = 0;
    if ((self->chroma == heif_chroma_interleaved_RGBA) || (self->chroma == heif_chroma_interleaved_RRGGBBAA_LE)) {
        stride_in = width * 4;
        with_alpha = 1;
    }
    else
        stride_in = width * 3;
    if (depth > 8)
        stride_in = stride_in * 2;
    if (stride_in * height != buffer.len) {
        PyBuffer_Release(&buffer);
        PyErr_SetString(PyExc_ValueError, "image plane size does not match data size");
        return NULL;
    }

    if (check_error(heif_image_add_plane(self->image, heif_channel_interleaved, width, height, depth))) {
        PyBuffer_Release(&buffer);
        return NULL;
    }

    plane_data = heif_image_get_plane(self->image, heif_channel_interleaved, &stride);
    if (!plane_data) {
        PyBuffer_Release(&buffer);
        PyErr_SetString(PyExc_RuntimeError, "heif_image_get_plane failed");
        return NULL;
    }

    int invalid_mode = 0;
    Py_BEGIN_ALLOW_THREADS
    uint8_t *out = plane_data;
    uint8_t *in = buffer.buf;
    uint16_t *out_word = (uint16_t *)plane_data;
    uint16_t *in_word = (uint16_t *)buffer.buf;
    if (!bgr_mode) {
        if ((depth_in == depth) && (stride_in == stride))
            memcpy(out, in, stride * height);
        else if ((depth_in == depth) && (stride_in != stride))
            for (int i = 0; i < height; i++)
                memcpy(out + stride * i, in + stride_in * i, stride_in);
        else if ((depth_in == 16) && (depth == 12) && (!with_alpha))
            for (int i = 0; i < height; i++) {
                for (int i2 = 0; i2 < width; i2++) {
                    out_word[i2 * 3 + 0] = in_word[i2 * 3 + 0] >> 4;
                    out_word[i2 * 3 + 1] = in_word[i2 * 3 + 1] >> 4;
                    out_word[i2 * 3 + 2] = in_word[i2 * 3 + 2] >> 4;
                }
                in_word += stride_in / 2;
                out_word += stride / 2;
            }
        else if ((depth_in == 16) && (depth == 12) && (with_alpha))
            for (int i = 0; i < height; i++) {
                for (int i2 = 0; i2 < width; i2++) {
                    out_word[i2 * 4 + 0] = in_word[i2 * 4 + 0] >> 4;
                    out_word[i2 * 4 + 1] = in_word[i2 * 4 + 1] >> 4;
                    out_word[i2 * 4 + 2] = in_word[i2 * 4 + 2] >> 4;
                    out_word[i2 * 4 + 3] = in_word[i2 * 4 + 3] >> 4;
                }
                in_word += stride_in / 2;
                out_word += stride / 2;
            }
        else if ((depth_in == 16) && (depth == 10) && (!with_alpha))
            for (int i = 0; i < height; i++) {
                for (int i2 = 0; i2 < width; i2++) {
                    out_word[i2 * 3 + 0] = in_word[i2 * 3 + 0] >> 6;
                    out_word[i2 * 3 + 1] = in_word[i2 * 3 + 1] >> 6;
                    out_word[i2 * 3 + 2] = in_word[i2 * 3 + 2] >> 6;
                }
                in_word += stride_in / 2;
                out_word += stride / 2;
            }
        else if ((depth_in == 16) && (depth == 10) && (with_alpha))
            for (int i = 0; i < height; i++) {
                for (int i2 = 0; i2 < width; i2++) {
                    out_word[i2 * 4 + 0] = in_word[i2 * 4 + 0] >> 6;
                    out_word[i2 * 4 + 1] = in_word[i2 * 4 + 1] >> 6;
                    out_word[i2 * 4 + 2] = in_word[i2 * 4 + 2] >> 6;
                    out_word[i2 * 4 + 3] = in_word[i2 * 4 + 3] >> 6;
                }
                in_word += stride_in / 2;
                out_word += stride / 2;
            }
        else
            invalid_mode = 1;
    }
    else {
        if ((depth_in == 8) && (depth == 8) && (!with_alpha))
            for (int i = 0; i < height; i++) {
                for (int i2 = 0; i2 < width; i2++) {
                    out[i2 * 3 + 0] = in[i2 * 3 + 2];
                    out[i2 * 3 + 1] = in[i2 * 3 + 1];
                    out[i2 * 3 + 2] = in[i2 * 3 + 0];
                }
                in += stride_in;
                out += stride;
            }
        else if ((depth_in == 8) &&(depth == 8) && (with_alpha))
            for (int i = 0; i < height; i++) {
                for (int i2 = 0; i2 < width; i2++) {
                    out[i2 * 4 + 0] = in[i2 * 4 + 2];
                    out[i2 * 4 + 1] = in[i2 * 4 + 1];
                    out[i2 * 4 + 2] = in[i2 * 4 + 0];
                    out[i2 * 4 + 3] = in[i2 * 4 + 3];
                }
                in += stride_in;
                out += stride;
            }
        else if ((depth_in == 16) && (depth == 10) && (!with_alpha))
            for (int i = 0; i < height; i++) {
                for (int i2 = 0; i2 < width; i2++) {
                    out_word[i2 * 3 + 0] = in_word[i2 * 3 + 2] >> 6;
                    out_word[i2 * 3 + 1] = in_word[i2 * 3 + 1] >> 6;
                    out_word[i2 * 3 + 2] = in_word[i2 * 3 + 0] >> 6;
                }
                in_word += stride_in / 2;
                out_word += stride / 2;
            }
        else if ((depth_in == 16) && (depth == 10) && (with_alpha))
            for (int i = 0; i < height; i++) {
                for (int i2 = 0; i2 < width; i2++) {
                    out_word[i2 * 4 + 0] = in_word[i2 * 4 + 2] >> 6;
                    out_word[i2 * 4 + 1] = in_word[i2 * 4 + 1] >> 6;
                    out_word[i2 * 4 + 2] = in_word[i2 * 4 + 0] >> 6;
                    out_word[i2 * 4 + 3] = in_word[i2 * 4 + 3] >> 6;
                }
                in_word += stride_in / 2;
                out_word += stride / 2;
            }
        else if ((depth_in == 16) && (depth == 12) && (!with_alpha))
            for (int i = 0; i < height; i++) {
                for (int i2 = 0; i2 < width; i2++) {
                    out_word[i2 * 3 + 0] = in_word[i2 * 3 + 2] >> 4;
                    out_word[i2 * 3 + 1] = in_word[i2 * 3 + 1] >> 4;
                    out_word[i2 * 3 + 2] = in_word[i2 * 3 + 0] >> 4;
                }
                in_word += stride_in / 2;
                out_word += stride / 2;
            }
        else if ((depth_in == 16) && (depth == 12) && (with_alpha))
            for (int i = 0; i < height; i++) {
                for (int i2 = 0; i2 < width; i2++) {
                    out_word[i2 * 4 + 0] = in_word[i2 * 4 + 2] >> 4;
                    out_word[i2 * 4 + 1] = in_word[i2 * 4 + 1] >> 4;
                    out_word[i2 * 4 + 2] = in_word[i2 * 4 + 0] >> 4;
                    out_word[i2 * 4 + 3] = in_word[i2 * 4 + 3] >> 4;
                }
                in_word += stride_in / 2;
                out_word += stride / 2;
            }
        else
            invalid_mode = 1;
    }
    Py_END_ALLOW_THREADS
    PyBuffer_Release(&buffer);
    if (invalid_mode) {
        PyErr_SetString(PyExc_ValueError, "invalid plane mode value");
        return NULL;
    }
    RETURN_NONE
}

static PyObject* _CtxWriteImage_add_plane_la(CtxWriteImageObject* self, PyObject* args) {
    /* (size), depth: int, depth_in: int, data: bytes */
    int width, height, depth, depth_in, stride_y, stride_alpha, stride_in;
    Py_buffer buffer;
    uint8_t *plane_data_y, *plane_data_alpha;

    if (!PyArg_ParseTuple(args, "(ii)iiy*", &width, &height, &depth, &depth_in, &buffer))
        return NULL;

    stride_in = width * 2;
    if (depth > 8)
        stride_in = stride_in * 2;
    if (stride_in * height != buffer.len) {
        PyBuffer_Release(&buffer);
        PyErr_SetString(PyExc_ValueError, "image plane size does not match data size");
        return NULL;
    }

    if (check_error(heif_image_add_plane(self->image, heif_channel_Y, width, height, depth))) {
        PyBuffer_Release(&buffer);
        return NULL;
    }

    if (check_error(heif_image_add_plane(self->image, heif_channel_Alpha, width, height, depth))) {
        PyBuffer_Release(&buffer);
        return NULL;
    }

    plane_data_y = heif_image_get_plane(self->image, heif_channel_Y, &stride_y);
    if (!plane_data_y) {
        PyBuffer_Release(&buffer);
        PyErr_SetString(PyExc_RuntimeError, "heif_image_get_plane(Y) failed");
        return NULL;
    }

    plane_data_alpha = heif_image_get_plane(self->image, heif_channel_Alpha, &stride_alpha);
    if (!plane_data_alpha) {
        PyBuffer_Release(&buffer);
        PyErr_SetString(PyExc_RuntimeError, "heif_image_get_plane(Alpha) failed");
        return NULL;
    }

    int invalid_mode = 0;
    Py_BEGIN_ALLOW_THREADS
    uint16_t *out_word_y = (uint16_t *)plane_data_y;
    uint16_t *out_word_alpha = (uint16_t *)plane_data_alpha;
    uint16_t *in_word = (uint16_t *)buffer.buf;
    if ((depth_in == depth) && (depth == 8)) {
        uint8_t *out_y = plane_data_y;
        uint8_t *out_alpha = plane_data_alpha;
        uint8_t *in = buffer.buf;
        for (int i = 0; i < height; i++) {
            for (int i2 = 0; i2 < width; i2++) {
                out_y[i2] = in[i2 * 2 + 0];
                out_alpha[i2] = in[i2 * 2 + 1];
            }
            in += stride_in;
            out_y += stride_y;
            out_alpha += stride_alpha;
        }
    }
    else if (depth_in == depth) {
        for (int i = 0; i < height; i++) {
            for (int i2 = 0; i2 < width; i2++) {
                out_word_y[i2] = in_word[i2 * 2 + 0];
                out_word_alpha[i2] = in_word[i2 * 2 + 1];
            }
            in_word += stride_in / 2;
            out_word_y += stride_y / 2;
            out_word_alpha += stride_alpha / 2;
        }
    }
    else if ((depth_in == 16) && (depth == 10))
        for (int i = 0; i < height; i++) {
            for (int i2 = 0; i2 < width; i2++) {
                out_word_y[i2] = in_word[i2 * 2 + 0] >> 6;
                out_word_alpha[i2] = in_word[i2 * 2 + 1] >> 6;
            }
            in_word += stride_in / 2;
            out_word_y += stride_y / 2;
            out_word_alpha += stride_alpha / 2;
        }
    else if ((depth_in == 16) && (depth == 12))
        for (int i = 0; i < height; i++) {
            for (int i2 = 0; i2 < width; i2++) {
                out_word_y[i2] = in_word[i2 * 2 + 0] >> 4;
                out_word_alpha[i2] = in_word[i2 * 2 + 1] >> 4;
            }
            in_word += stride_in / 2;
            out_word_y += stride_y / 2;
            out_word_alpha += stride_alpha / 2;
        }
    else
        invalid_mode = 1;
    Py_END_ALLOW_THREADS
    PyBuffer_Release(&buffer);
    if (invalid_mode) {
        PyErr_SetString(PyExc_ValueError, "invalid plane mode value");
        return NULL;
    }
    RETURN_NONE
}

static PyObject* _CtxWriteImage_add_plane_l(CtxWriteImageObject* self, PyObject* args) {
    /* (size), depth: int, depth_in: int, data: bytes */
    int width, height, depth, depth_in, stride, stride_in;
    Py_buffer buffer;
    uint8_t *plane_data;

    if (!PyArg_ParseTuple(args, "(ii)iiy*", &width, &height, &depth, &depth_in, &buffer))
        return NULL;

    stride_in = width;
    if (depth > 8)
        stride_in = stride_in * 2;
    if (stride_in * height != buffer.len) {
        PyBuffer_Release(&buffer);
        PyErr_SetString(PyExc_ValueError, "image plane size does not match data size");
        return NULL;
    }

    if (check_error(heif_image_add_plane(self->image, heif_channel_Y, width, height, depth))) {
        PyBuffer_Release(&buffer);
        return NULL;
    }

    plane_data = heif_image_get_plane(self->image, heif_channel_Y, &stride);
    if (!plane_data) {
        PyBuffer_Release(&buffer);
        PyErr_SetString(PyExc_RuntimeError, "heif_image_get_plane(Y) failed");
        return NULL;
    }

    int invalid_mode = 0;
    Py_BEGIN_ALLOW_THREADS
    uint8_t *out = plane_data;
    uint8_t *in = buffer.buf;
    uint16_t *out_word = (uint16_t *)plane_data;
    uint16_t *in_word = (uint16_t *)buffer.buf;
    if ((depth_in == depth) && (stride_in == stride))
        memcpy(out, in, stride * height);
    else if ((depth_in == depth) && (stride_in != stride))
        for (int i = 0; i < height; i++)
            memcpy(out + stride * i, in + stride_in * i, stride_in);
    else if ((depth_in == 16) && (depth == 10))
        for (int i = 0; i < height; i++) {
            for (int i2 = 0; i2 < width; i2++)
                out_word[i2] = in_word[i2] >> 6;
            in_word += stride_in / 2;
            out_word += stride / 2;
        }
    else if ((depth_in == 16) && (depth == 12))
        for (int i = 0; i < height; i++) {
            for (int i2 = 0; i2 < width; i2++)
                out_word[i2] = in_word[i2] >> 4;
            in_word += stride_in / 2;
            out_word += stride / 2;
        }
    else
        invalid_mode = 1;
    Py_END_ALLOW_THREADS
    PyBuffer_Release(&buffer);
    if (invalid_mode) {
        PyErr_SetString(PyExc_ValueError, "invalid plane mode value");
        return NULL;
    }
    RETURN_NONE
}

static PyObject* _CtxWriteImage_set_icc_profile(CtxWriteImageObject* self, PyObject* args) {
    /* type: str, color_profile: bytes */
    const char* type;
    Py_buffer buffer;
    struct heif_error error;

    if (!PyArg_ParseTuple(args, "sy*", &type, &buffer))
        return NULL;

    error = heif_image_set_raw_color_profile(self->image, type, buffer.buf, (int)buffer.len);
    PyBuffer_Release(&buffer);
    if (check_error(error))
        return NULL;
    RETURN_NONE
}

static PyObject* _CtxWriteImage_set_nclx_profile(CtxWriteImageObject* self, PyObject* args) {
    /* color_primaries: int, transfer_characteristics: int, matrix_coefficients: int, full_range_flag: int */
    struct heif_error error;
    int color_primaries, transfer_characteristics, matrix_coefficients, full_range_flag;

    if (!PyArg_ParseTuple(args, "iiii",
        &color_primaries, &transfer_characteristics, &matrix_coefficients, &full_range_flag))
        return NULL;

    struct heif_color_profile_nclx* nclx_color_profile = heif_nclx_color_profile_alloc();
    nclx_color_profile->color_primaries = color_primaries;
    nclx_color_profile->transfer_characteristics = transfer_characteristics;
    nclx_color_profile->matrix_coefficients = matrix_coefficients;
    nclx_color_profile->full_range_flag = full_range_flag;
    error = heif_image_set_nclx_color_profile(self->image, nclx_color_profile);
    heif_nclx_color_profile_free(nclx_color_profile);
    if (check_error(error))
        return NULL;
    RETURN_NONE
}

static PyObject* _CtxWriteImage_encode(CtxWriteImageObject* self, PyObject* args) {
    /* ctx: CtxWriteObject, primary: int */
    CtxWriteObject* ctx_write;
    int primary;
    struct heif_error error;
    struct heif_encoding_options* options;

    if (!PyArg_ParseTuple(args, "Oi", (PyObject*)&ctx_write, &primary))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    options = heif_encoding_options_alloc();
    error = heif_context_encode_image(ctx_write->ctx, self->image, ctx_write->encoder, options, &self->handle);
    heif_encoding_options_free(options);
    Py_END_ALLOW_THREADS
    if (check_error(error))
        return NULL;

    if (primary)
        heif_context_set_primary_image(ctx_write->ctx, self->handle);
    RETURN_NONE
}

static PyObject* _CtxWriteImage_set_exif(CtxWriteImageObject* self, PyObject* args) {
    /* ctx: CtxWriteObject, data: bytes */
    CtxWriteObject* ctx_write;
    Py_buffer buffer;
    struct heif_error error;

    if (!PyArg_ParseTuple(args, "Oy*", (PyObject*)&ctx_write, &buffer))
        return NULL;

    error = heif_context_add_exif_metadata(ctx_write->ctx, self->handle, buffer.buf, (int)buffer.len);
    PyBuffer_Release(&buffer);
    if (check_error(error))
        return NULL;
    RETURN_NONE
}

static PyObject* _CtxWriteImage_set_xmp(CtxWriteImageObject* self, PyObject* args) {
    /* ctx: CtxWriteObject, data: bytes */
    CtxWriteObject* ctx_write;
    Py_buffer buffer;
    struct heif_error error;

    if (!PyArg_ParseTuple(args, "Oy*", (PyObject*)&ctx_write, &buffer))
        return NULL;

    error = heif_context_add_XMP_metadata(ctx_write->ctx, self->handle, buffer.buf, (int)buffer.len);
    PyBuffer_Release(&buffer);
    if (check_error(error))
        return NULL;
    RETURN_NONE
}

static PyObject* _CtxWriteImage_set_metadata(CtxWriteImageObject* self, PyObject* args) {
    /* ctx: CtxWriteObject, type: str, content_type: str, data: bytes */
    CtxWriteObject* ctx_write;
    const char *type, *content_type;
    Py_buffer buffer;
    struct heif_error error;

    if (!PyArg_ParseTuple(args, "Ossy*", (PyObject*)&ctx_write, &type, &content_type, &buffer))
        return NULL;

    error = heif_context_add_generic_metadata(ctx_write->ctx, self->handle, buffer.buf, (int)buffer.len, type, content_type);
    PyBuffer_Release(&buffer);
    if (check_error(error))
        return NULL;
    RETURN_NONE
}

static PyObject* _CtxWriteImage_encode_thumbnail(CtxWriteImageObject* self, PyObject* args) {
    /* ctx: CtxWriteObject, thumb_box: int */
    struct heif_error error;
    struct heif_image_handle* thumb_handle;
    struct heif_encoding_options* options;
    CtxWriteObject* ctx_write;
    int thumb_box;

    if (!PyArg_ParseTuple(args, "Oi", (PyObject*)&ctx_write, &thumb_box))
        return NULL;

    Py_BEGIN_ALLOW_THREADS
    options = heif_encoding_options_alloc();
    error = heif_context_encode_thumbnail(
        ctx_write->ctx,
        self->image,
        self->handle,
        ctx_write->encoder,
        options,
        thumb_box,
        &thumb_handle);
    heif_encoding_options_free(options);
    Py_END_ALLOW_THREADS
    if (check_error(error))
        return NULL;
    heif_image_handle_release(thumb_handle);
    RETURN_NONE
}

static struct PyMethodDef _CtxWriteImage_methods[] = {
    {"add_plane", (PyCFunction)_CtxWriteImage_add_plane, METH_VARARGS},
    {"add_plane_l", (PyCFunction)_CtxWriteImage_add_plane_l, METH_VARARGS},
    {"add_plane_la", (PyCFunction)_CtxWriteImage_add_plane_la, METH_VARARGS},
    {"set_icc_profile", (PyCFunction)_CtxWriteImage_set_icc_profile, METH_VARARGS},
    {"set_nclx_profile", (PyCFunction)_CtxWriteImage_set_nclx_profile, METH_VARARGS},
    {"encode", (PyCFunction)_CtxWriteImage_encode, METH_VARARGS},
    {"set_exif", (PyCFunction)_CtxWriteImage_set_exif, METH_VARARGS},
    {"set_xmp", (PyCFunction)_CtxWriteImage_set_xmp, METH_VARARGS},
    {"set_metadata", (PyCFunction)_CtxWriteImage_set_metadata, METH_VARARGS},
    {"encode_thumbnail", (PyCFunction)_CtxWriteImage_encode_thumbnail, METH_VARARGS},
    {NULL, NULL}
};

/* =========== CtxWrite ======== */

static struct heif_error ctx_write_callback(struct heif_context* ctx, const void* data, size_t size, void* userdata) {
    *((PyObject**)userdata) = PyBytes_FromStringAndSize((char*)data, size);
    return heif_error_no;
}

static struct heif_writer ctx_writer = { .writer_api_version = 1, .write = &ctx_write_callback };

static void _CtxWrite_destructor(CtxWriteObject* self) {
    if (self->data)
        free(self->data);
    if (self->encoder)
        heif_encoder_release(self->encoder);
    heif_context_free(self->ctx);
    PyObject_Del(self);
}

static PyObject* _CtxWrite_set_parameter(CtxWriteObject* self, PyObject* args) {
    char *key, *value;
    if (!PyArg_ParseTuple(args, "ss", &key, &value))
        return NULL;
    if (check_error(heif_encoder_set_parameter(self->encoder, key, value)))
        return NULL;
    RETURN_NONE
}

static PyObject* _CtxWriteImage_create(CtxWriteObject* self, PyObject* args) {
    /* (size), color: int, chroma: int, premultiplied: int */
    struct heif_image* image;
    int width, height, colorspace, chroma, premultiplied;
    if (!PyArg_ParseTuple(args, "(ii)iii", &width, &height, &colorspace, &chroma, &premultiplied))
        return NULL;

    if (check_error(heif_image_create(width, height, colorspace, chroma, &image)))
        return NULL;
    if (premultiplied)
        heif_image_set_premultiplied_alpha(image, 1);

    CtxWriteImageObject* ctx_write_image = PyObject_New(CtxWriteImageObject, &CtxWriteImage_Type);
    if (!ctx_write_image) {
        heif_image_release(image);
        PyErr_SetString(PyExc_RuntimeError, "could not create CtxWriteImage object");
        return NULL;
    }
    ctx_write_image->chroma = chroma;
    ctx_write_image->image = image;
    ctx_write_image->handle = NULL;
    return (PyObject*)ctx_write_image;
}

static PyObject* _CtxWrite_finalize(CtxWriteObject* self) {
    PyObject *ret = NULL;
    struct heif_error error = heif_context_write(self->ctx, &ctx_writer, &ret);
    if (!check_error(error)) {
        if (ret != NULL)
            return ret;
        PyErr_SetString(PyExc_RuntimeError, "Unknown runtime or memory error");
    }
    return NULL;
}

static struct PyMethodDef _CtxWrite_methods[] = {
    {"set_parameter", (PyCFunction)_CtxWrite_set_parameter, METH_VARARGS},
    {"create_image", (PyCFunction)_CtxWriteImage_create, METH_VARARGS},
    {"finalize", (PyCFunction)_CtxWrite_finalize, METH_NOARGS},
    {NULL, NULL}
};

/* =========== CtxImage ======== */

int get_stride(CtxImageObject *ctx_image) {
    int stride = ctx_image->width * 3;
    if (ctx_image->alpha)
        stride = ctx_image->width * 4;
    if ((ctx_image->bits > 8) && (!ctx_image->hdr_to_8bit))
        stride = stride * 2;
    return stride;
}

static void _CtxImage_destructor(CtxImageObject* self) {
    if (self->heif_image)
        heif_image_release(self->heif_image);
    if (self->handle)
        heif_image_handle_release(self->handle);
    Py_DECREF(self->file_bytes);
    PyObject_Del(self);
}

PyObject* _CtxImage(struct heif_image_handle* handle, int hdr_to_8bit, int bgr_mode, int postprocess,
                    int reload_size, int primary, PyObject* file_bytes) {
    CtxImageObject *ctx_image = PyObject_New(CtxImageObject, &CtxImage_Type);
    if (!ctx_image) {
        heif_image_handle_release(handle);
        RETURN_NONE
    }
    ctx_image->width = heif_image_handle_get_width(handle);
    ctx_image->height = heif_image_handle_get_height(handle);
    strcpy(ctx_image->mode, bgr_mode ? "BGR" : "RGB");
    ctx_image->alpha = heif_image_handle_has_alpha_channel(handle);
    if (ctx_image->alpha)
        strcat(ctx_image->mode, heif_image_handle_is_premultiplied_alpha(handle) ? "a" : "A");
    ctx_image->bits = heif_image_handle_get_luma_bits_per_pixel(handle);
    if ((ctx_image->bits > 8) && (!hdr_to_8bit))
        strcat(ctx_image->mode, ";16");
    ctx_image->hdr_to_8bit = hdr_to_8bit;
    ctx_image->bgr_mode = bgr_mode;
    ctx_image->handle = handle;
    ctx_image->heif_image = NULL;
    ctx_image->data = NULL;
    ctx_image->postprocess = postprocess;
    ctx_image->reload_size = reload_size;
    ctx_image->primary = primary;
    ctx_image->file_bytes = file_bytes;
    ctx_image->stride = get_stride(ctx_image);
    Py_INCREF(file_bytes);
    return (PyObject*)ctx_image;
}

static PyObject* _CtxImage_size_mode(CtxImageObject* self, void* closure) {
    return Py_BuildValue("(ii)s", self->width, self->height, self->mode);
}

static PyObject* _CtxImage_primary(CtxImageObject* self, void* closure) {
    return Py_BuildValue("i", self->primary);
}

static PyObject* _CtxImage_bit_depth(CtxImageObject* self, void* closure) {
    return Py_BuildValue("i", self->bits);
}

static PyObject* _CtxImage_color_profile(CtxImageObject* self, void* closure) {
    enum heif_color_profile_type profile_type = heif_image_handle_get_color_profile_type(self->handle);
    if (profile_type == heif_color_profile_type_not_present)
        return PyDict_New();

    if (profile_type == heif_color_profile_type_nclx) {
        struct heif_color_profile_nclx* nclx_profile;
        if (check_error(heif_image_handle_get_nclx_color_profile(self->handle, &nclx_profile)))
            return NULL;

        PyObject* result = PyDict_New();
        __PyDict_SetItemString(result, "type", PyUnicode_FromString("nclx"));
        PyObject* d = PyDict_New();
        __PyDict_SetItemString(d, "color_primaries", PyLong_FromLong(nclx_profile->color_primaries));
        __PyDict_SetItemString(d, "transfer_characteristics", PyLong_FromLong(nclx_profile->transfer_characteristics));
        __PyDict_SetItemString(d, "matrix_coefficients", PyLong_FromLong(nclx_profile->matrix_coefficients));
        __PyDict_SetItemString(d, "full_range_flag", PyLong_FromLong(nclx_profile->full_range_flag));
        __PyDict_SetItemString(d, "color_primary_red_x", PyFloat_FromDouble(nclx_profile->color_primary_red_x));
        __PyDict_SetItemString(d, "color_primary_red_y", PyFloat_FromDouble(nclx_profile->color_primary_red_y));
        __PyDict_SetItemString(d, "color_primary_green_x", PyFloat_FromDouble(nclx_profile->color_primary_green_x));
        __PyDict_SetItemString(d, "color_primary_green_y", PyFloat_FromDouble(nclx_profile->color_primary_green_y));
        __PyDict_SetItemString(d, "color_primary_blue_x", PyFloat_FromDouble(nclx_profile->color_primary_blue_x));
        __PyDict_SetItemString(d, "color_primary_blue_y", PyFloat_FromDouble(nclx_profile->color_primary_blue_y));
        __PyDict_SetItemString(d, "color_primary_white_x", PyFloat_FromDouble(nclx_profile->color_primary_white_x));
        __PyDict_SetItemString(d, "color_primary_white_y", PyFloat_FromDouble(nclx_profile->color_primary_white_y));
        heif_nclx_color_profile_free(nclx_profile);
        __PyDict_SetItemString(result, "data", d);
        return result;
    }

    PyObject* result = PyDict_New();
    __PyDict_SetItemString(
        result, "type", PyUnicode_FromString(profile_type == heif_color_profile_type_rICC ? "rICC" : "prof"));
    size_t size = heif_image_handle_get_raw_color_profile_size(self->handle);
    if (!size)
        __PyDict_SetItemString(result, "data", PyBytes_FromString(""));
    else {
        void* data = malloc(size);
        if (!data) {
            Py_DECREF(result);
            result = NULL;
            PyErr_SetString(PyExc_OSError, "Out of Memory");
        }
        else {
            if (!check_error(heif_image_handle_get_raw_color_profile(self->handle, data)))
                __PyDict_SetItemString(result, "data", PyBytes_FromStringAndSize(data, size));
            else {
                Py_DECREF(result);
                result = NULL;
            }
            free(data);
        }
    }
    return result;
}

static PyObject* _CtxImage_metadata(CtxImageObject* self, void* closure) {
    PyObject *meta_item_info;
    const char *type, *content_type;
    size_t size;
    void* data;
    struct heif_error error;

    int n_metas = heif_image_handle_get_number_of_metadata_blocks(self->handle, NULL);
    if (!n_metas)
        return PyList_New(0);

    heif_item_id* meta_ids  = (heif_item_id*)malloc(n_metas * sizeof(heif_item_id));
    if (!meta_ids) {
        PyErr_SetString(PyExc_OSError, "Out of Memory");
        return NULL;
    }
    n_metas = heif_image_handle_get_list_of_metadata_block_IDs(self->handle, NULL, meta_ids, n_metas);
    PyObject* meta_list = PyList_New(n_metas);
    if (!meta_list) {
        free(meta_ids);
        PyErr_SetString(PyExc_OSError, "Out of Memory");
        return NULL;
    }

    for (int i = 0; i < n_metas; i++) {
        meta_item_info = NULL;
        type = heif_image_handle_get_metadata_type(self->handle, meta_ids[i]);
        content_type = heif_image_handle_get_metadata_content_type(self->handle, meta_ids[i]);
        size = heif_image_handle_get_metadata_size(self->handle, meta_ids[i]);
        data = malloc(size);
        if (data) {
            error = heif_image_handle_get_metadata(self->handle, meta_ids[i], data);
            if (error.code == heif_error_Ok) {
                meta_item_info = PyDict_New();
                __PyDict_SetItemString(meta_item_info, "type", PyUnicode_FromString(type));
                __PyDict_SetItemString(meta_item_info, "content_type", PyUnicode_FromString(content_type));
                __PyDict_SetItemString(meta_item_info, "data", PyBytes_FromStringAndSize((char*)data, size));
            }
            free(data);
        }
        if (!meta_item_info) {
            meta_item_info = Py_None;
            Py_INCREF(meta_item_info);
        }
        PyList_SET_ITEM(meta_list, i, meta_item_info);
    }
    free(meta_ids);
    return meta_list;
}

static PyObject* _CtxImage_thumbnails(CtxImageObject* self, void* closure) {
    int n_images = heif_image_handle_get_number_of_thumbnails(self->handle);
    if (n_images == 0)
        return PyList_New(0);
    heif_item_id* images_ids = (heif_item_id*)malloc(n_images * sizeof(heif_item_id));
    if (!images_ids)
        return PyList_New(0);

    n_images = heif_image_handle_get_list_of_thumbnail_IDs(self->handle, images_ids, n_images);
    PyObject* images_list = PyList_New(n_images);
    if (!images_list) {
        free(images_ids);
        return PyList_New(0);
    }

    struct heif_image_handle* handle;
    struct heif_error error;
    for (int i = 0; i < n_images; i++) {
        int box = 0;
        error = heif_image_handle_get_thumbnail(self->handle, images_ids[i], &handle);
        if (error.code == heif_error_Ok) {
            int width = heif_image_handle_get_width(handle);
            int height = heif_image_handle_get_height(handle);
            heif_image_handle_release(handle);
            box = width >= height ? width : height;
        }
        PyList_SET_ITEM(images_list, i, PyLong_FromSsize_t(box));
    }
    free(images_ids);
    return images_list;
}

int decode_image(CtxImageObject* self) {
    struct heif_error error;

    Py_BEGIN_ALLOW_THREADS
    struct heif_decoding_options *decode_options = heif_decoding_options_alloc();
    decode_options->convert_hdr_to_8bit = self->hdr_to_8bit;
    int chroma;
    if ((self->bits == 8) || (self->hdr_to_8bit))
        chroma = self->alpha ? heif_chroma_interleaved_RGBA : heif_chroma_interleaved_RGB;
    else
        chroma = self->alpha ? heif_chroma_interleaved_RRGGBBAA_LE : heif_chroma_interleaved_RRGGBB_LE;
    error = heif_decode_image(self->handle, &self->heif_image, heif_colorspace_RGB, chroma, decode_options);
    heif_decoding_options_free(decode_options);
    Py_END_ALLOW_THREADS
    if (check_error(error))
        return 0;

    int stride;
    self->data = heif_image_get_plane(self->heif_image, heif_channel_interleaved, &stride);
    if (!self->data) {
        heif_image_release(self->heif_image);
        self->heif_image = NULL;
        PyErr_SetString(PyExc_RuntimeError, "heif_image_get_plane failed");
        return 0;
    }

    int decoded_width = heif_image_get_primary_width(self->heif_image);
    int decoded_height = heif_image_get_primary_height(self->heif_image);
    if (self->reload_size) {
        self->width = decoded_width;
        self->height = decoded_height;
    }
    else if ((self->width > decoded_width) || (self->height > decoded_height)) {
        heif_image_release(self->heif_image);
        self->heif_image = NULL;
        PyErr_Format(PyExc_ValueError,
                    "corrupted image(dimensions in header: (%d, %d), decoded dimensions: (%d, %d)). "
                    "Set ALLOW_INCORRECT_HEADERS to True if you need to load it.",
                    self->width, self->height, decoded_width, decoded_height);
        return 0;
    }

    if (!self->postprocess) {
        self->stride = stride;
        return 1;
    }
    self->stride = get_stride(self);

    if ((self->bgr_mode) || (self->stride != stride) || ((self->bits > 8) && (!self->hdr_to_8bit))) {
        int invalid_mode = 0;
        Py_BEGIN_ALLOW_THREADS
        if ((self->hdr_to_8bit) || (self->bits == 8)) {
            uint8_t *in = (uint8_t*)self->data;
            uint8_t *out = (uint8_t*)self->data;
            if (!self->bgr_mode)    // just remove stride
                for (int i = 0; i < self->height; i++) {
                    memmove(out, in, self->stride); // possible will change to memcpy and set -D_FORTIFY_SOURCE=0
                    in += stride;
                    out += self->stride;
                }
            else {                  // remove stride && convert to BGR(A)
                uint8_t tmp;
                if (!self->alpha)
                    for (int i = 0; i < self->height; i++) {
                        for (int i2 = 0; i2 < self->width; i2++) {
                            tmp = in[i2 * 3 + 0];
                            out[i2 * 3 + 0] = in[i2 * 3 + 2];
                            out[i2 * 3 + 1] = in[i2 * 3 + 1];
                            out[i2 * 3 + 2] = tmp;
                        }
                        in += stride;
                        out += self->stride;
                    }
                else
                    for (int i = 0; i < self->height; i++) {
                        for (int i2 = 0; i2 < self->width; i2++) {
                            tmp = in[i2 * 4 + 0];
                            out[i2 * 4 + 0] = in[i2 * 4 + 2];
                            out[i2 * 4 + 1] = in[i2 * 4 + 1];
                            out[i2 * 4 + 2] = tmp;
                            out[i2 * 4 + 3] = in[i2 * 4 + 3];
                        }
                        in += stride;
                        out += self->stride;
                    }
            }
        }
        else {
            uint16_t *in = (uint16_t*)self->data;
            uint16_t *out = (uint16_t*)self->data;
            uint16_t tmp;
            if ((self->bits == 10) && (self->alpha) && (!self->bgr_mode))
                for (int i = 0; i < self->height; i++) {
                    for (int i2 = 0; i2 < self->width; i2++) {
                        out[i2 * 4 + 0] = in[i2 * 4 + 0] << 6;
                        out[i2 * 4 + 1] = in[i2 * 4 + 1] << 6;
                        out[i2 * 4 + 2] = in[i2 * 4 + 2] << 6;
                        out[i2 * 4 + 3] = in[i2 * 4 + 3] << 6;
                    }
                    in += stride / 2;
                    out += self->stride / 2;
                }
            else if ((self->bits == 10) && (self->alpha) && (self->bgr_mode))
                for (int i = 0; i < self->height; i++) {
                    for (int i2 = 0; i2 < self->width; i2++) {
                        tmp = in[i2 * 4 + 0];
                        out[i2 * 4 + 0] = in[i2 * 4 + 2] << 6;
                        out[i2 * 4 + 1] = in[i2 * 4 + 1] << 6;
                        out[i2 * 4 + 2] = tmp << 6;
                        out[i2 * 4 + 3] = in[i2 * 4 + 3] << 6;
                    }
                    in += stride / 2;
                    out += self->stride / 2;
                }
            else if ((self->bits == 10) && (!self->alpha) && (!self->bgr_mode))
                for (int i = 0; i < self->height; i++) {
                    for (int i2 = 0; i2 < self->width; i2++) {
                        out[i2 * 3 + 0] = in[i2 * 3 + 0] << 6;
                        out[i2 * 3 + 1] = in[i2 * 3 + 1] << 6;
                        out[i2 * 3 + 2] = in[i2 * 3 + 2] << 6;
                    }
                    in += stride / 2;
                    out += self->stride / 2;
                }
            else if ((self->bits == 10) && (!self->alpha) && (self->bgr_mode))
                for (int i = 0; i < self->height; i++) {
                    for (int i2 = 0; i2 < self->width; i2++) {
                        tmp = in[i2 * 3 + 0];
                        out[i2 * 3 + 0] = in[i2 * 3 + 2] << 6;
                        out[i2 * 3 + 1] = in[i2 * 3 + 1] << 6;
                        out[i2 * 3 + 2] = tmp << 6;
                    }
                    in += stride / 2;
                    out += self->stride / 2;
                }
            else if ((self->bits == 12) && (self->alpha) && (!self->bgr_mode))
                for (int i = 0; i < self->height; i++) {
                    for (int i2 = 0; i2 < self->width; i2++) {
                        out[i2 * 4 + 0] = in[i2 * 4 + 0] << 4;
                        out[i2 * 4 + 1] = in[i2 * 4 + 1] << 4;
                        out[i2 * 4 + 2] = in[i2 * 4 + 2] << 4;
                        out[i2 * 4 + 3] = in[i2 * 4 + 3] << 4;
                    }
                    in += stride / 2;
                    out += self->stride / 2;
                }
            else if ((self->bits == 12) && (self->alpha) && (self->bgr_mode)) {
                for (int i = 0; i < self->height; i++) {
                    for (int i2 = 0; i2 < self->width; i2++) {
                        tmp = in[i2 * 4 + 0];
                        out[i2 * 4 + 0] = in[i2 * 4 + 2] << 4;
                        out[i2 * 4 + 1] = in[i2 * 4 + 1] << 4;
                        out[i2 * 4 + 2] = tmp << 4;
                        out[i2 * 4 + 3] = in[i2 * 4 + 3] << 4;
                    }
                    in += stride / 2;
                    out += self->stride / 2;
                }
            }
            else if ((self->bits == 12) && (!self->alpha) && (!self->bgr_mode))
                for (int i = 0; i < self->height; i++) {
                    for (int i2 = 0; i2 < self->width; i2++) {
                        out[i2 * 3 + 0] = in[i2 * 3 + 0] << 4;
                        out[i2 * 3 + 1] = in[i2 * 3 + 1] << 4;
                        out[i2 * 3 + 2] = in[i2 * 3 + 2] << 4;
                    }
                    in += stride / 2;
                    out += self->stride / 2;
                }
            else if ((self->bits == 12) && (!self->alpha) && (self->bgr_mode))
                for (int i = 0; i < self->height; i++) {
                    for (int i2 = 0; i2 < self->width; i2++) {
                        tmp = in[i2 * 3 + 0];
                        out[i2 * 3 + 0] = in[i2 * 3 + 2] << 4;
                        out[i2 * 3 + 1] = in[i2 * 3 + 1] << 4;
                        out[i2 * 3 + 2] = tmp << 4;
                    }
                    in += stride / 2;
                    out += self->stride / 2;
                }
            else
                invalid_mode = 1;
        }
        Py_END_ALLOW_THREADS
        if (invalid_mode) {
            PyErr_SetString(PyExc_ValueError, "invalid plane mode value");
            return 0;
        }
    }
    return 1;
}

static PyObject* _CtxImage_stride(CtxImageObject* self, void* closure) {
    if (!self->data)
        if (!decode_image(self))
            return NULL;
    return PyLong_FromSsize_t(self->stride);
}

static PyObject* _CtxImage_data(CtxImageObject* self, void* closure) {
    if (!self->data)
        if (!decode_image(self))
            return NULL;
    return PyMemoryView_FromMemory((char*)self->data, self->stride * self->height, PyBUF_READ);
}

static struct PyGetSetDef _CtxImage_getseters[] = {
    {"size_mode", (getter)_CtxImage_size_mode, NULL, NULL, NULL},
    {"primary", (getter)_CtxImage_primary, NULL, NULL, NULL},
    {"bit_depth", (getter)_CtxImage_bit_depth, NULL, NULL, NULL},
    {"color_profile", (getter)_CtxImage_color_profile, NULL, NULL, NULL},
    {"metadata", (getter)_CtxImage_metadata, NULL, NULL, NULL},
    {"thumbnails", (getter)_CtxImage_thumbnails, NULL, NULL, NULL},
    {"stride", (getter)_CtxImage_stride, NULL, NULL, NULL},
    {"data", (getter)_CtxImage_data, NULL, NULL, NULL},
    {NULL, NULL, NULL, NULL, NULL}
};

/* =========== Functions ======== */

static PyObject* _CtxWrite(PyObject* self, PyObject* args) {
    /* compression_format: int, quality: int */
    struct heif_encoder* encoder;
    struct heif_error error;
    int compression_format, quality;

    if (!PyArg_ParseTuple(args, "ii", &compression_format, &quality))
        return NULL;

    struct heif_context* ctx = heif_context_alloc();
    error = heif_context_get_encoder_for_format(ctx, compression_format, &encoder);
    if (check_error(error)) {
        heif_context_free(ctx);
        return NULL;
    }

    if (quality == -1)
        error = heif_encoder_set_lossless(encoder, 1);
    else if (quality >= 0)
        error = heif_encoder_set_lossy_quality(encoder, quality);
    if (check_error(error)) {
        heif_encoder_release(encoder);
        heif_context_free(ctx);
        return NULL;
    }

    CtxWriteObject* ctx_write = PyObject_New(CtxWriteObject, &CtxWrite_Type);
    if (!ctx_write) {
        heif_encoder_release(encoder);
        heif_context_free(ctx);
        PyErr_SetString(PyExc_RuntimeError, "could not create CtxWrite object");
        return NULL;
    }
    ctx_write->ctx = ctx;
    ctx_write->encoder = encoder;
    ctx_write->size = 0;
    ctx_write->data = NULL;
    return (PyObject*)ctx_write;
}

static PyObject* _load_file(PyObject* self, PyObject* args) {
    int hdr_to_8bit, threads_count, bgr_mode, postprocess, reload_size;
    PyObject *heif_bytes;

    if (!PyArg_ParseTuple(args,
                          "Oiiiii",
                          &heif_bytes,
                          &threads_count,
                          &hdr_to_8bit,
                          &bgr_mode,
                          &postprocess,
                          &reload_size))
        return NULL;

    struct heif_context* heif_ctx = heif_context_alloc();
    if (check_error(heif_context_read_from_memory_without_copy(
                        heif_ctx, (void*)PyBytes_AS_STRING(heif_bytes), PyBytes_GET_SIZE(heif_bytes), NULL))) {
        heif_context_free(heif_ctx);
        return NULL;
    }

    #if LIBHEIF_HAVE_VERSION(1,13,0)
        heif_context_set_max_decoding_threads(heif_ctx, threads_count);
    #endif

    heif_item_id primary_image_id;
    if (check_error(heif_context_get_primary_image_ID(heif_ctx, &primary_image_id))) {
        heif_context_free(heif_ctx);
        return NULL;
    }

    int n_images = heif_context_get_number_of_top_level_images(heif_ctx);
    heif_item_id* images_ids = (heif_item_id*)malloc(n_images * sizeof(heif_item_id));
    if (!images_ids) {
        heif_context_free(heif_ctx);
        PyErr_SetString(PyExc_OSError, "Out of Memory");
        return NULL;
    }
    n_images = heif_context_get_list_of_top_level_image_IDs(heif_ctx, images_ids, n_images);
    PyObject* images_list = PyList_New(n_images);
    if (!images_list) {
        free(images_ids);
        heif_context_free(heif_ctx);
        PyErr_SetString(PyExc_OSError, "Out of Memory");
        return NULL;
    }

    struct heif_image_handle* handle;
    struct heif_error error;
    for (int i = 0; i < n_images; i++) {
        int primary = 0;
        if (images_ids[i] == primary_image_id) {
            error = heif_context_get_primary_image_handle(heif_ctx, &handle);
            primary = 1;
        }
        else
            error = heif_context_get_image_handle(heif_ctx, images_ids[i], &handle);
        if (error.code == heif_error_Ok)
            PyList_SET_ITEM(images_list,
                            i,
                            _CtxImage(handle, hdr_to_8bit, bgr_mode, postprocess, reload_size, primary, heif_bytes));
        else {
            Py_INCREF(Py_None);
            PyList_SET_ITEM(images_list, i, Py_None);
        }
    }
    free(images_ids);
    heif_context_free(heif_ctx);
    return images_list;
}

/* =========== Module =========== */

static PyMethodDef heifMethods[] = {
    {"CtxWrite", (PyCFunction)_CtxWrite, METH_VARARGS},
    {"load_file", (PyCFunction)_load_file, METH_VARARGS},
    {NULL, NULL}
};

static PyTypeObject CtxWriteImage_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "CtxWriteImage",
    .tp_basicsize = sizeof(CtxWriteImageObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)_CtxWriteImage_destructor,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = _CtxWriteImage_methods,
};

static PyTypeObject CtxWrite_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "CtxWrite",
    .tp_basicsize = sizeof(CtxWriteObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)_CtxWrite_destructor,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_methods = _CtxWrite_methods,
};

static PyTypeObject CtxImage_Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "CtxImage",
    .tp_basicsize = sizeof(CtxImageObject),
    .tp_itemsize = 0,
    .tp_dealloc = (destructor)_CtxImage_destructor,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_getset = _CtxImage_getseters,
};

static int setup_module(PyObject* m) {
    PyObject* d = PyModule_GetDict(m);

    if (PyType_Ready(&CtxWriteImage_Type) < 0)
        return -1;

    if (PyType_Ready(&CtxWrite_Type) < 0)
        return -1;

    if (PyType_Ready(&CtxImage_Type) < 0)
        return -1;

    const struct heif_encoder_descriptor* encoder_descriptor;
    const char* x265_version = "";
    if (heif_context_get_encoder_descriptors(NULL, heif_compression_HEVC, NULL, &encoder_descriptor, 1))
        x265_version = heif_encoder_descriptor_get_name(encoder_descriptor);
    const char* aom_version = "";
    if (heif_context_get_encoder_descriptors(NULL, heif_compression_AV1, NULL, &encoder_descriptor, 1))
        aom_version = heif_encoder_descriptor_get_name(encoder_descriptor);

    PyObject* version_dict = PyDict_New();
    __PyDict_SetItemString(version_dict, "libheif", PyUnicode_FromString(heif_get_version()));
    __PyDict_SetItemString(version_dict, "HEIF", PyUnicode_FromString(x265_version));
    __PyDict_SetItemString(version_dict, "AVIF", PyUnicode_FromString(aom_version));

    if (__PyDict_SetItemString(d, "lib_info", version_dict) < 0)
        return -1;
    return 0;
}

PyMODINIT_FUNC PyInit__pillow_heif(void) {
    static PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        "_pillow_heif", /* m_name */
        NULL,           /* m_doc */
        -1,             /* m_size */
        heifMethods,    /* m_methods */
    };

    PyObject* m = PyModule_Create(&module_def);
    if (setup_module(m) < 0)
        return NULL;
    return m;
}
