import zlib
import re
import png  # Ensure you have installed pypng: pip install pypng

def from_hex_str(hex_str):
    """Converts a hex string to raw bytes."""
    return bytes(int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2))

def convert_terminal_to_image(
    terminal_file='terminal.txt',
    output_path='reconstructed.png',
    bit_depth=4,
    size=(128, 128)
):
    """
    Reads compressed hex data from a terminal file, reconstructs the grayscale image, and saves it as a PNG.
    """
    assert 1 <= bit_depth <= 7, "bit_depth must be between 1 and 7"

    try:
        # Step 1: Read hex data from terminal.txt
        with open(terminal_file, 'r') as f:
            hex_lines = [
                line.strip() for line in f
                if line.strip()
                and not line.strip().startswith('[FEATHER]')
                and not re.fullmatch(r'-+', line.strip())
                and re.fullmatch(r'[0-9a-fA-F]+', line.strip())
            ]

        hex_data = ''.join(hex_lines)
        compressed_data = from_hex_str(hex_data)

        # Step 2: Decompress
        data = zlib.decompress(compressed_data)

        # Step 3: Decode pixels from bit-packed data
        total_pixels = size[0] * size[1]
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

        # Step 4: Convert to 2D image and save as PNG
        image = []
        for i in range(size[1]):
            row = pixels[i * size[0]:(i + 1) * size[0]]
            image.append(row)

        with open(output_path, 'wb') as f:
            writer = png.Writer(size[0], size[1], greyscale=True, bitdepth=8)
            writer.write(f, image)

        print(f"Reconstructed image saved to '{output_path}'")

    except Exception as e:
        print(f"Failed to reconstruct image: {e}")

convert_terminal_to_image()