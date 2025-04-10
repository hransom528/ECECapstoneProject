import time
import math

def send_file(hex_data, handler):
    """
    Sends a base16 (hex) encoded string over LoRa using the provided handler.
    Each packet contains handler.max_packet_size bytes = max_packet_size hex characters.
    """
    packet_list = [hex_data[i:i + handler.max_packet_size] for i in range(0, len(hex_data), handler.max_packet_size)]
    
    print(f"Total packets to send: {len(packet_list)}")

    for packet in packet_list:
        print(packet.encode('ascii'))
        handler.rfm9x.send(packet.encode('ascii'))
        time.sleep(1)

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
