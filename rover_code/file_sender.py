import os
import math
import time
import zlib

def send_file(file_path, handler):
    """
    Reads the file at file_path, compresses its contents using zlib,
    splits it into packets based on handler.max_packet_size, and sends
    each packet with a header over the LoRa interface.
    
    First, a header packet is sent containing:
      - 3 bytes: "HDR" signature
      - 2 bytes: total packet count (big-endian)
      - 1 byte: file type (e.g., 1 for image)
      - 1 byte: compression flag (1 if compressed, 0 otherwise)
      
    Then each data packet is sent with a header:
      - 2 bytes: sequence number (big-endian)
      - 2 bytes: total packet count (big-endian)
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False

    # Compress the data to reduce packet count.
    compressed_data = zlib.compress(data)
    total_packets = math.ceil(len(compressed_data) / handler.max_packet_size)
    print(f"Sending {total_packets} data packets...")

    # Construct header packet.
    # Header format: b"HDR" + total_packets (2 bytes) + file_type (1 byte) + compression flag (1 byte)
    file_type = 1         # For example, 1 indicates an image file.
    compression_flag = 1  # 1 indicates the file is compressed.
    header_packet = b"HDR" + total_packets.to_bytes(2, 'big') + file_type.to_bytes(1, 'big') + compression_flag.to_bytes(1, 'big')
    handler.rfm9x.send(header_packet)
    print("Sent header packet.")
    time.sleep(0.1)  # Small delay before sending data packets.

    # Send each data packet.
    for i in range(total_packets):
        start = i * handler.max_packet_size
        end = start + handler.max_packet_size
        packet_data = compressed_data[start:end]
        # Create data packet header: sequence number and total packet count.
        data_header = i.to_bytes(2, 'big') + total_packets.to_bytes(2, 'big')
        packet = data_header + packet_data
        handler.rfm9x.send(packet)
        print(f"Sent data packet #{i+1}")
        time.sleep(0.1)  # Delay to allow LoRa hardware to finish sending.
    return True

def send_packet(packet_index, file_path, handler):
    """
    Resends a single packet specified by packet_index.
    Useful when the basestation identifies dropped packets.
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False

    compressed = zlib.compress(data)
    total_packets = math.ceil(len(compressed) / handler.max_packet_size)

    if packet_index >= total_packets:
        print(f"Invalid packet index {packet_index}. Total packets: {total_packets}")
        return False

    start = packet_index * handler.max_packet_size
    end = start + handler.max_packet_size
    packet_data = compressed[start:end]
    header = packet_index.to_bytes(2, 'big') + total_packets.to_bytes(2, 'big')
    packet = header + packet_data
    handler.rfm9x.send(packet)
    print(f"Resent packet {packet_index}")
    return True
