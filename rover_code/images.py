from PIL import Image
import os
import math
import zlib

def load_image_variable_bpp(image_path, bit_depth=2, size=(256, 256)):
    """
    Loads an image, applies Floyd–Steinberg dithering to grayscale, scales it
    to the given bit depth (2–7), and returns packed binary data.
    """
    assert 1 <= bit_depth <= 7, "bit_depth must be between 1 and 7"

    try:
        with Image.open(image_path) as img:
            img = img.convert("L").resize(size)
            img_data = img.load()
            width, height = img.size
            max_val = (1 << bit_depth) - 1

            # Dithering and quantization
            for y in range(height):
                for x in range(width):
                    old_pixel = img_data[x, y]
                    new_pixel_val = round(old_pixel * max_val / 255)
                    new_pixel = int(new_pixel_val * (255 // max_val))
                    img_data[x, y] = new_pixel
                    error = old_pixel - new_pixel

                    if x + 1 < width:
                        img_data[x + 1, y] = clip(img_data[x + 1, y] + error * 7 / 16)
                    if x - 1 >= 0 and y + 1 < height:
                        img_data[x - 1, y + 1] = clip(img_data[x - 1, y + 1] + error * 3 / 16)
                    if y + 1 < height:
                        img_data[x, y + 1] = clip(img_data[x, y + 1] + error * 5 / 16)
                    if x + 1 < width and y + 1 < height:
                        img_data[x + 1, y + 1] = clip(img_data[x + 1, y + 1] + error * 1 / 16)

            # Flatten pixels after dithering
            pixels = [img_data[x, y] * max_val // 255 for y in range(height) for x in range(width)]

            packed_bytes = bytearray()
            buffer = 0
            bits_filled = 0

            for val in pixels:
                buffer = (buffer << bit_depth) | val
                bits_filled += bit_depth

                while bits_filled >= 8:
                    bits_filled -= 8
                    packed_bytes.append((buffer >> bits_filled) & 0xFF)

            if bits_filled > 0:
                buffer = buffer << (8 - bits_filled)
                packed_bytes.append(buffer & 0xFF)

            return packed_bytes
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def clip(value):
    return int(max(0, min(255, value)))


def compress_and_save(data, output_path):
    compressed = zlib.compress(data)
    with open(output_path, 'wb') as f:
        f.write(compressed)
    print(f"Saved compressed binary to {output_path}")
    return compressed  # Return for metrics


def load_bin_and_reconstruct_image(bin_path, bit_depth=4, size=(256, 256), image_show=False):
    """
    Reconstructs an image from compressed binary grayscale data.
    """
    assert 1 <= bit_depth <= 7, "bit_depth must be between 1 and 7"

    try:
        with open(bin_path, 'rb') as f:
            compressed_data = f.read()

        data = zlib.decompress(compressed_data)

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

        if image_show:
            img = Image.new("L", size)
            img.putdata(pixels)
            img.show()

    except Exception as e:
        print(f"Failed to reconstruct image: {e}")


def sizer(len_data):
    packets = len_data / 224
    print(f"Number of packets to send: {math.ceil(packets)}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_image_path = os.path.join(script_dir, "img", "img_2.png")
    bin_output_path = os.path.join(script_dir, "output.bin")

    bit_depth = 4  # Change to 2, 3, 4, etc.

    a = 128

    data = load_image_variable_bpp(input_image_path, bit_depth=bit_depth, size=(a,a))

    if data:
        compressed = compress_and_save(data, bin_output_path)

        # Optional preview
        # print("Binary Output (first 256 bits):")
        # binary_string = ''.join(f'{byte:08b}' for byte in compressed)
        # print(binary_string[:256])
        print(f"Compressed bytes written: {len(compressed)}")
        sizer(len(compressed))

        # Reconstruct and display
        load_bin_and_reconstruct_image(bin_output_path, bit_depth=bit_depth, size=(a,a), image_show=False)
    else:
        print("Image conversion failed.")
