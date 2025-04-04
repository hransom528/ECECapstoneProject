import time

def receive_photo(rfm9x):
    """
    Receives packets over LoRa and dumps their raw contents to img.bin.

    Each packet is expected to have a 4-byte header:
      - First 2 bytes: sequence number (big-endian)
      - Next 2 bytes: total number of packets (big-endian)

    The function reassembles the packets in the correct order
    and writes the combined binary data to img.bin.
    """
    RECEIVE_TIMEOUT = 60.0         # Overall timeout for the complete transmission.
    INTER_PACKET_TIMEOUT = 2.0     # Timeout for each receive() call.
    POST_RECEIVE_TIMEOUT = 5.0     # Additional time to wait after the last received packet.

    print("Receiving raw image data...")

    packets = {}
    expected_total = None
    start_time = time.time()
    last_packet_time = None

    while True:
        current_time = time.time()
        # If we've received at least one packet and no new packet has arrived within POST_RECEIVE_TIMEOUT, stop waiting.
        if last_packet_time is not None and (current_time - last_packet_time) > POST_RECEIVE_TIMEOUT:
            print("No new packet received for a while, ending reception.")
            break

        # Check if overall timeout has been reached.
        if (current_time - start_time) > RECEIVE_TIMEOUT:
            print("Overall receive timeout reached.")
            break

        packet = rfm9x.receive(timeout=INTER_PACKET_TIMEOUT)
        if packet:
            last_packet_time = current_time
            if len(packet) < 4:
                print("Received short packet, skipping.")
                continue

            seq = int.from_bytes(packet[0:2], "big")
            total = int.from_bytes(packet[2:4], "big")
            if expected_total is None:
                expected_total = total
                print(f"Expecting {expected_total} packets.")

            packets[seq] = packet[4:]
            print(f"Received packet {seq + 1}/{total}")

            if len(packets) == expected_total:
                print("All packets received.")
                break
        # If no packet is received, the loop will check timeouts and try again.
    
    if expected_total is None or len(packets) != expected_total:
        print(f"Incomplete receive: {len(packets)}/{expected_total if expected_total else 0} packets.")
        return

    # Reassemble raw binary data in order and save to disk
    raw_data = b"".join(packets[i] for i in range(expected_total))
    with open("img.bin", "wb") as f:
        f.write(raw_data)

    print("Raw image data saved to img.bin.")
