from cpython.mem cimport PyMem_Malloc, PyMem_Free

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
    cdef char* buffer = <char*> PyMem_Malloc(length * sizeof(char))

    if buffer == NULL:
        raise MemoryError()

    try:
        for j in range(length):
            buffer[j] = characters[raw_pixels[j]]
        return bytes(buffer[:length]).decode('ascii')
    finally:
        PyMem_Free(buffer)