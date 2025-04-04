# camera.py

import time
import zlib
import math
from PIL import Image

def receive_photo(rfm9x, size=(128, 128), bit_depth=4):
    """
    Receives packets containing compressed, bit-packed image data over LoRa,
    reassembles and decompresses the image, and displays the reconstructed image.

    Each packet is expected to have a 4-byte header:
      - First 2 bytes: sequence number (big-endian integer)
      - Next 2 bytes: total number of packets (big-endian integer)
    
    The image is reconstructed from the decompressed bit stream based on the 
    provided size and bit depth. Pixel values are scaled to the full 0-255 range.
    """
    # Define timeouts (in seconds)
    RECEIVE_TIMEOUT = 5.0
    INTER_PACKET_TIMEOUT = 0.5

    print("Receiving photo...")
    
    screenshot_packets = {}
    expected_total = None
    start_time = time.time()
    last_packet_time = time.time()
    
    # Collect packets until timeout or until all expected packets are received.
    while time.time() - start_time < RECEIVE_TIMEOUT:
        packet = rfm9x.receive(timeout=INTER_PACKET_TIMEOUT)
        if packet:
            if len(packet) < 4:
                print("Received packet too short, skipping.")
                continue

            # Parse header: first 2 bytes = sequence number, next 2 = total packet count.
            seq = int.from_bytes(packet[0:2], "big")
            total = int.from_bytes(packet[2:4], "big")
            if expected_total is None:
                expected_total = total
                print(f"Expecting {expected_total} packets.")
            data_part = packet[4:]
            screenshot_packets[seq] = data_part
            print(f"Received packet {seq + 1}/{total}")
            last_packet_time = time.time()
            if len(screenshot_packets) == expected_total:
                break
        else:
            # If we've received some packets and no new packet comes in a while, break out.
            if screenshot_packets and (time.time() - last_packet_time > INTER_PACKET_TIMEOUT):
                break

    if expected_total is None or len(screenshot_packets) != expected_total:
        print("Failed to receive all packets. Received {}/{} packets.".format(
            len(screenshot_packets), expected_total if expected_total is not None else 0))
        return

    # Reassemble the complete compressed data in order.
    compressed = b"".join(screenshot_packets[i] for i in range(expected_total))
    try:
        decompressed = zlib.decompress(compressed)
    except Exception as e:
        print(f"Decompression failed: {e}")
        return

    # Calculate total pixels and set up variables for unpacking the bit stream.
    total_pixels = size[0] * size[1]
    max_val = (1 << bit_depth) - 1
    scale = 255 // max_val
    pixels = []
    buffer = 0
    bits_in_buffer = 0

    # Unpack the bit-packed stream into individual pixel values.
    for byte in decompressed:
        buffer = (buffer << 8) | byte
        bits_in_buffer += 8
        while bits_in_buffer >= bit_depth and len(pixels) < total_pixels:
            bits_in_buffer -= bit_depth
            val = (buffer >> bits_in_buffer) & max_val
            pixels.append(val * scale)
        buffer &= (1 << bits_in_buffer) - 1

    if len(pixels) != total_pixels:
        print("Warning: Expected {} pixels but got {} pixels.".format(total_pixels, len(pixels)))

    # Create and display the grayscale image.
    img = Image.new("L", size)
    img.putdata(pixels)
    img.show()
    print("Screenshot image displayed.")
