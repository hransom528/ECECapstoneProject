import os
import math
import zlib
import png


def clip(value):
    return int(max(0, min(255, round(value))))


def read_image_to_grayscale(image_path):
    reader = png.Reader(image_path)
    width, height, rows, info = reader.read()
    rows = list(rows)
    image = []

    if info.get('greyscale', False):
        for row in rows:
            image.append(list(row))
    else:
        channels = info.get('planes', 3)
        for row in rows:
            row = list(row)
            new_row = []
            for i in range(0, len(row), channels):
                R = row[i]
                G = row[i + 1]
                B = row[i + 2]
                gray = int(round(0.299 * R + 0.587 * G + 0.114 * B))
                new_row.append(gray)
            image.append(new_row)

    return image, width, height


def resize_image(image, new_size):
    new_width, new_height = new_size
    orig_height = len(image)
    orig_width = len(image[0])
    new_image = []

    for j in range(new_height):
        orig_j = int(j * orig_height / new_height)
        row = []
        for i in range(new_width):
            orig_i = int(i * orig_width / new_width)
            row.append(image[orig_j][orig_i])
        new_image.append(row)

    return new_image


def convert_image(image_path, bit_depth=4, size=(256, 256), dithering=True):
    assert 1 <= bit_depth <= 7, "bit_depth must be between 1 and 7"

    image, _, _ = read_image_to_grayscale(image_path)
    image = resize_image(image, size)
    width, height = size
    max_val = (1 << bit_depth) - 1

    if dithering:
        for y in range(height):
            for x in range(width):
                old_pixel = image[y][x]
                new_pixel_val = round(old_pixel * max_val / 255)
                new_pixel = int(new_pixel_val * (255 // max_val))
                image[y][x] = new_pixel
                error = old_pixel - new_pixel

                if x + 1 < width:
                    image[y][x + 1] = clip(image[y][x + 1] + error * 7 / 16)
                if x - 1 >= 0 and y + 1 < height:
                    image[y + 1][x - 1] = clip(image[y + 1][x - 1] + error * 3 / 16)
                if y + 1 < height:
                    image[y + 1][x] = clip(image[y + 1][x] + error * 5 / 16)
                if x + 1 < width and y + 1 < height:
                    image[y + 1][x + 1] = clip(image[y + 1][x + 1] + error * 1 / 16)

    # Flatten image
    flat_pixels = []
    for row in image:
        for pixel in row:
            quantized = pixel * max_val // 255
            flat_pixels.append(quantized)

    # Pack into bytes
    packed_bytes = bytearray()
    buffer = 0
    bits_filled = 0

    for val in flat_pixels:
        buffer = (buffer << bit_depth) | val
        bits_filled += bit_depth

        while bits_filled >= 8:
            bits_filled -= 8
            packed_bytes.append((buffer >> bits_filled) & 0xFF)

    if bits_filled > 0:
        buffer = buffer << (8 - bits_filled)
        packed_bytes.append(buffer & 0xFF)

    compressed = zlib.compress(packed_bytes)
    hex_output = compressed.hex()

    print(f"Image converted successfully. Total hex length: {len(hex_output)}")

    return hex_output
