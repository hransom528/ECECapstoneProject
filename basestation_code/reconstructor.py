import zlib
import re
import png

import base64  # make sure this is imported at the top

def from_base64_str(b64_str):
    """
    Converts a base64 string to raw bytes.
    """
    return base64.b64decode(b64_str)

def from_hex_str(hex_str):
    return bytes(int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2))


def unpack_pixels(data, bit_depth, width, height):
    total_pixels = width * height
    max_val = (1 << bit_depth) - 1
    scale = 255 // max_val

    pixels = []
    buffer = 0
    bits_in_buffer = 0

    for byte in data:
        buffer = (buffer << 8) | byte
        bits_in_buffer += 8

        while bits_in_buffer >= bit_depth and len(pixels) < total_pixels:
            bits_in_buffer -= bit_depth
            val = (buffer >> bits_in_buffer) & max_val
            pixels.append(val * scale)

        buffer &= (1 << bits_in_buffer) - 1

    if len(pixels) < total_pixels:
        raise ValueError(f"Not enough pixel data: expected {total_pixels}, got {len(pixels)}")

    return pixels


def convert_terminal_to_image(
    terminal_file='terminal.txt',
    output_path='reconstructed.png',
    bit_depth=4,
    size=(64,64)
):
    try:
        with open(terminal_file, 'r') as f:
            lines = f.readlines()

        cleaned_lines = []
        for line in lines:
            line = line.replace("'", "")
            line = line.split(":")[-1] if ":" in line else line
            cleaned_lines.append(line.strip())

        hex_lines = [
            line for line in cleaned_lines
            if line
            and not line.startswith('[FEATHER]')
            # and not re.fullmatch(r'-+', line)
            # and re.fullmatch(r'[0-9a-fA-F]+', line)
        ]

        hex_data = ''.join(hex_lines)
        # compressed_data = from_hex_str(hex_data)
        compressed_data = from_base64_str(hex_data)

        raw_data = zlib.decompress(compressed_data)

        width, height = size
        pixels = unpack_pixels(raw_data, bit_depth, width, height)

        # Split flat pixels into rows
        image = [pixels[i * width:(i + 1) * width] for i in range(height)]

        with open(output_path, 'wb') as f:
            writer = png.Writer(width, height, greyscale=True, bitdepth=8)
            writer.write(f, image)

        print(f"Reconstructed image saved to '{output_path}'")

    except Exception as e:
        print(f"Failed to reconstruct image: {e}")


convert_terminal_to_image()
