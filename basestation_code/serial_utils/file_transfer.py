import zlib
import re
import png
from logger import log_to_file

def reconstruct_image_from_hex(hex_data, output_path="reconstructed.png", bit_depth=4, image_size=(128, 128)):
    if not re.fullmatch(r'[0-9a-fA-F]+', hex_data):
        raise ValueError("Invalid hex data received.")

    compressed_data = bytes.fromhex(hex_data)
    decompressed = zlib.decompress(compressed_data)

    width, height = image_size
    total_pixels = width * height
    max_val = (1 << bit_depth) - 1
    scale = 255 // max_val

    pixels = []
    buffer = 0
    bits_in_buffer = 0

    for byte in decompressed:
        buffer = (buffer << 8) | byte
        bits_in_buffer += 8

        while bits_in_buffer >= bit_depth and len(pixels) < total_pixels:
            bits_in_buffer -= bit_depth
            val = (buffer >> bits_in_buffer) & max_val
            pixels.append(val * scale)

        buffer &= (1 << bits_in_buffer) - 1

    image = [pixels[i * width:(i + 1) * width] for i in range(height)]

    with open(output_path, 'wb') as f:
        writer = png.Writer(width, height, greyscale=True, bitdepth=8)
        writer.write(f, image)

    log_to_file(f"[FEATHER] Image reconstruction complete. Saved to '{output_path}'")
    print(f"[FEATHER] Image reconstruction complete. Saved to '{output_path}'")
