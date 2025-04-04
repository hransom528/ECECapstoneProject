import time
INTER_PACKET_TIMEOUT = 0.5  # Max wait between packets (LoRa has ~0.2s delay per packet)

def network_test(rfm9x, count):
    test_message = f"ECHO {count} ABABABABABABABABAIOEEIOJGEIOJGEOIGJOEIJGEOIJGEIOJGEOIJGEOIJGEOIJGEOIJGIOEJGIOEJG"
    message = test_message.encode('utf-8')

    print(f"[TEST] Sending network test command: {test_message}")
    rfm9x.send(message)

    print(f"[TEST] Waiting for {count} packets...")


    received_packets = 0
    total_bytes = 0
    start_time = time.time()
    last_packet_time = time.time()

    while received_packets < count:
        packet = rfm9x.receive(timeout=INTER_PACKET_TIMEOUT)
        if packet:
            try:
                decoded = packet.decode('utf-8').strip()
                print(f"[RECEIVED] {decoded}")
                received_packets += 1
                total_bytes += len(packet)
                last_packet_time = time.time()
            except UnicodeDecodeError:
                print("[ERROR] Received invalid UTF-8 data")
        else:
            if time.time() - last_packet_time > INTER_PACKET_TIMEOUT:
                print("[TIMEOUT] No more packets received.")
                break

    end_time = time.time()
    duration = end_time - start_time

    if received_packets == 0:
        print("[RESULT] No packets received.")
    else:
        kbps = (total_bytes / 1024) / duration
        print(f"[RESULT] Received {received_packets}/{count} packets in {duration:.2f} seconds")
        print(f"[RESULT] Throughput: {kbps:.2f} KB/s")