import zlib
import re
import png
from PIL import Image
import io


def from_hex_str(hex_str):
    return bytes(int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2))


def convert_terminal_to_image(
    terminal_file='terminal.txt',
    output_path='reconstructed.png'
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
            and not re.fullmatch(r'-+', line)
            and re.fullmatch(r'[0-9a-fA-F]+', line)
        ]

        hex_data = ''.join(hex_lines)
        compressed_data = from_hex_str(hex_data)

        jpg_bytes = zlib.decompress(compressed_data)

        jpg_image = Image.open(io.BytesIO(jpg_bytes)).convert('L')

        jpg_image.save(output_path)

        print(f"Reconstructed image saved to '{output_path}'")

    except Exception as e:
        print(f"Failed to reconstruct image: {e}")


convert_terminal_to_image()
