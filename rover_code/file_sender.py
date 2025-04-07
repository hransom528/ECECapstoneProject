def send_file(file_path, handler):
    import os
    import math
    import time
    import zlib

    try:
        with open(file_path, 'rb') as f:
            data = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False

    compressed_data = zlib.compress(data)
    total_packets = math.ceil(len(compressed_data) / handler.max_packet_size)
    print(f"Sending {total_packets} data packets...")

    # Define file type codes (expand as needed)
    FILE_TYPES = {
        1: "image",
        2: "text",
        3: "binary",
    }

    # File header values
    file_type = 1         # Example: 1 = image
    compression_flag = 1  # 1 = compressed, 0 = raw

    # Send binary header packet
    header_packet = b"HDR" + total_packets.to_bytes(2, 'big') + file_type.to_bytes(1, 'big') + compression_flag.to_bytes(1, 'big')
    handler.rfm9x.send(header_packet)

    # Print human-readable header info
    print("[HEADER INFO]")
    print(f"  File type       : {FILE_TYPES.get(file_type, 'unknown')} (code {file_type})")
    print(f"  Compressed      : {'yes' if compression_flag else 'no'}")
    print(f"  Total packets   : {total_packets}")
    print("Sent header packet.")
    time.sleep(0.1)
    
    def to_hex_str(data):
        hex_chars = '0123456789abcdef'
        hex_str = ''
        for byte in data:
            high = hex_chars[(byte >> 4) & 0x0F]
            low = hex_chars[byte & 0x0F]
            hex_str += high + low
        return hex_str


    # Send each data packet with headers
    for i in range(total_packets):
        start = i * handler.max_packet_size
        end = start + handler.max_packet_size
        packet_data = compressed_data[start:end]
        # data_header = i.to_bytes(2, 'big') + total_packets.to_bytes(2, 'big')
        # packet = data_header + packet_data
        print(to_hex_str(packet_data))
        handler.rfm9x.send(packet_data)
        print(f"Sent data packet #{i+1}")
        time.sleep(0.1)
    
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
    # header = packet_index.to_bytes(2, 'big') + total_packets.to_bytes(2, 'big')
    # packet = header + packet_data
    handler.rfm9x.send(packet_data)
    print(f"Resent packet {packet_index}")
    return True
