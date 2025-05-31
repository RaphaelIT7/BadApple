from cpython.mem cimport PyMem_Malloc, PyMem_Free
from cython.parallel cimport prange
import numpy as np
cimport numpy as np
from libc.string cimport memcpy
from libc.stdint cimport int64_t, uint64_t, uint16_t, uint8_t, uintptr_t
from libc.stddef cimport size_t
import sys

cdef bytes grey_chars = (
    b"@#8&B%MW*oahkbdpqwmZO0QLCJUYXzcvunxrjft/|()1{}[]?-_+~<>!lI;:\",^`'." b" "
)

cdef char characters[256]
cdef int index

# We calculate the gray scale here so that we don't need to do it later for each pixel.
for brightness in range(256):
    index = int((brightness / 255) * (len(grey_chars) - 1))
    characters[<int>brightness] = <char>grey_chars[index]

def pixel_to_ascii(const unsigned char[:] raw_pixels):
    cdef Py_ssize_t length = raw_pixels.shape[0]
    cdef Py_ssize_t j
    cdef char* buffer = <char*>PyMem_Malloc(length * sizeof(char))

    if buffer == NULL:
        raise MemoryError()

    try:
        for j in prange(length, nogil=True):
            buffer[j] = characters[raw_pixels[j]]
        return bytes(buffer[:length]).decode('ascii')
    finally:
        PyMem_Free(buffer)

ctypedef struct DLDataType:
    uint8_t code
    uint8_t bits
    uint16_t lanes

ctypedef struct DLContext:
    int device_type
    int device_id

ctypedef struct DLTensor:
    void* data
    DLContext ctx
    int ndim
    DLDataType dtype
    int64_t* shape
    int64_t* strides
    uint64_t byte_offset

# Debugging why decord has a memory leak
def cython_copy_to_numpy(uintptr_t handle_addr, uintptr_t dst_addr, size_t nbytes, uintptr_t handle_addr2):
    cdef DLTensor* handle = <DLTensor*>handle_addr
    cdef char* dst = <char*>dst_addr

    if handle == NULL or handle.data == NULL:
        print("Invalid handle or data pointer")
        return -1

    cdef const char* src = <const char*>handle.data + handle.byte_offset

    memcpy(dst, src, nbytes) # Why tf would this cause a memory leak of 16GB

    return 0