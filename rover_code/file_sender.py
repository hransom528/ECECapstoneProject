import time
import math

def send_file(hex_data, handler):
    """
    Sends a base16 (hex) encoded string over LoRa using the provided handler.
    Each packet contains handler.max_packet_size bytes = max_packet_size hex characters.
    """
    packet_list = [hex_data[i:i + handler.max_packet_size] for i in range(0, len(hex_data), handler.max_packet_size)]
    
    print(f"Total packets to send: {len(packet_list)}")

    # set delay before sending ACK
    handler.rfm9x.ack_delay = 0.1
    # set node addresses
    handler.rfm9x.node = 1
    handler.rfm9x.destination = 2

    for packet in packet_list:
        print(packet.encode('ascii'))
        handler.rfm9x.send_with_ack(packet.encode('ascii'))
        time.sleep(0.1)

    return True