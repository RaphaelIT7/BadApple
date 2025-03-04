cdef grey_chars = [
    '@', '#', '8', '&', 'B', '%', 'M', 'W', '*', 'o', 'a', 'h', 'k', 'b', 'd', 'p', 'q',
    'w', 'm', 'Z', 'O', '0', 'Q', 'L', 'C', 'J', 'U', 'Y', 'X', 'z', 'c', 'v', 'u', 'n',
    'x', 'r', 'j', 'f', 't', '/', '|', '(', ')', '1', '{', '}', '[', ']', '?', '-', '_',
    '+', '~', '<', '>', 'i', '!', 'l', 'I', ';', ':', ',', '"', '^', '`', '\'', '.', ' '
]

cdef list characters = []

# We calculate the gray scale here so that we don't need to do it later for each pixel.
for i in range(256):
    brightness = i
    index = int((brightness / 255) * (len(grey_chars) - 1))
    characters.append(grey_chars[index])

def pixel_to_ascii(raw_pixels):
    cdef list ascii_pixels = []
    for pixel in raw_pixels:
        ascii_pixels.append(characters[pixel])
    
    return "".join(ascii_pixels)