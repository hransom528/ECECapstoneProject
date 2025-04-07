import os
import math

try:
    import zlib
except ImportError:
    zlib = None
    print("Warning: zlib module is not available. Compression-related features may not work.")

try:
    import png
except ImportError:
    png = None
    print("Warning: png module is not available. PNG-related features will be disabled.")


def clip(value):
    return int(max(0, min(255, round(value))))

def read_image_to_grayscale(image_path):
    """
    Reads a PNG file using pypng and returns a 2D list of grayscale values (0-255).
    If the image is not already grayscale, converts each pixel using the luminance formula.
    """
    try:
        reader = png.Reader(image_path)
        width, height, rows, info = reader.read()
        rows = list(rows)
        image = []
        if info.get('greyscale', False):
            # Image is already grayscale.
            for row in rows:
                image.append(list(row))
        else:
            channels = info.get('planes', 3)
            for row in rows:
                row = list(row)
                new_row = []
                for i in range(0, len(row), channels):
                    R = row[i]
                    G = row[i+1]
                    B = row[i+2]
                    # Standard luminosity formula.
                    gray = int(round(0.299 * R + 0.587 * G + 0.114 * B))
                    new_row.append(gray)
                image.append(new_row)
        return image, width, height
    except Exception as e:
        print(f"Error reading image: {e}")
        return None, None, None

def resize_image(image, new_size):
    """
    Resizes a 2D list 'image' to new_size (width, height)
    using nearest-neighbor interpolation.
    """
    new_width, new_height = new_size
    orig_height = len(image)
    orig_width = len(image[0])
    new_image = []
    for j in range(new_height):
        orig_j = int(j * orig_height / new_height)
        if orig_j >= orig_height:
            orig_j = orig_height - 1
        row = []
        for i in range(new_width):
            orig_i = int(i * orig_width / new_width)
            if orig_i >= orig_width:
                orig_i = orig_width - 1
            row.append(image[orig_j][orig_i])
        new_image.append(row)
    return new_image

def load_image_variable_bpp(image_path, bit_depth=2, size=(256, 256)):
    """
    Loads an image, converts to grayscale if needed, applies Floyd–Steinberg
    dithering to quantize to the given bit depth, and returns packed binary data.
    """
    assert 1 <= bit_depth <= 7, "bit_depth must be between 1 and 7"

    try:
        image, orig_width, orig_height = read_image_to_grayscale(image_path)
        if image is None:
            return None

        # Resize image to target dimensions.
        image = resize_image(image, size)
        height = len(image)
        width = len(image[0])
        max_val = (1 << bit_depth) - 1

        # Apply Floyd–Steinberg dithering and quantization.
        for y in range(height):
            for x in range(width):
                old_pixel = image[y][x]
                new_pixel_val = round(old_pixel * max_val / 255)
                new_pixel = int(new_pixel_val * (255 // max_val))
                image[y][x] = new_pixel
                error = old_pixel - new_pixel

                if x + 1 < width:
                    image[y][x+1] = clip(image[y][x+1] + error * 7 / 16)
                if x - 1 >= 0 and y + 1 < height:
                    image[y+1][x-1] = clip(image[y+1][x-1] + error * 3 / 16)
                if y + 1 < height:
                    image[y+1][x] = clip(image[y+1][x] + error * 5 / 16)
                if x + 1 < width and y + 1 < height:
                    image[y+1][x+1] = clip(image[y+1][x+1] + error * 1 / 16)

        # Flatten and quantize pixels.
        pixels = []
        for row in image:
            for pixel in row:
                quantized = pixel * max_val // 255
                pixels.append(quantized)

        # Pack pixel values into a bytearray.
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

def compress_and_save(data, output_path):
    """
    Compresses binary data using zlib and writes it to a file.
    """
    compressed = zlib.compress(data)
    with open(output_path, 'wb') as f:
        f.write(compressed)
    print(f"Saved compressed binary to {output_path}")
    return compressed

def load_bin_and_reconstruct_image(bin_path, bit_depth=4, size=(256, 256), image_show=False):
    """
    Reconstructs an image from compressed binary grayscale data.
    If image_show is True, saves the reconstructed image as a PNG file.
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
            # Convert flat pixel list into 2D image.
            image = []
            for i in range(size[1]):
                row = pixels[i*size[0]:(i+1)*size[0]]
                image.append(row)
            output_image_path = "reconstructed.png"
            with open(output_image_path, 'wb') as f:
                writer = png.Writer(size[0], size[1], greyscale=True, bitdepth=8)
                writer.write(f, image)
            print(f"Reconstructed image saved to {output_image_path}")

    except Exception as e:
        print(f"Failed to reconstruct image: {e}")

def sizer(len_data):
    packets = len_data / 224
    print(f"Number of packets to send: {math.ceil(packets)}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_image_path = os.path.join(script_dir, "img", "img.png")
    bin_output_path = os.path.join(script_dir, "output.bin")

    bit_depth = 4  # Adjust bit depth as desired.
    a = 128  # Image dimensions (a x a)

    data = load_image_variable_bpp(input_image_path, bit_depth=bit_depth, size=(a, a))

    if data:
        compressed = compress_and_save(data, bin_output_path)
        print(f"Compressed bytes written: {len(compressed)}")
        sizer(len(compressed))
        load_bin_and_reconstruct_image(bin_output_path, bit_depth=bit_depth, size=(a, a), image_show=True)
    else:
        print("Image conversion failed.")
