import time
from lora_setup import get_lora_radio

# Configuration parameters for the network test
PACKET_SIZES = [64, 128]   # Valid packet sizes in bytes
packet_size_index = 0      # Using the first packet size for this example
TEST_DURATION = 30         # Duration of the test in seconds
PING_INTERVAL = 0.5        # Time between pings (seconds)
TIMEOUT = 2.0              # Timeout waiting for response (seconds)

def run_network_test():
    """Run a combined LoRa network test measuring both latency and throughput."""
    print(f"\nStarting LoRa network test with packet size {PACKET_SIZES[packet_size_index]} bytes")
    
    # Initialize the LoRa radio transceiver
    rfm9x = get_lora_radio()
    
    # Initialize statistics counters
    sent_packets = 0
    received_packets = 0
    total_latency = 0.0
    dropped_packets = 0

    start_time = time.monotonic()
    
    while time.monotonic() - start_time < TEST_DURATION:
        # Create a payload that contains a ping message with a timestamp
        timestamp = time.monotonic()
        message = f"ping|{timestamp}"
        pad_length = PACKET_SIZES[packet_size_index] - len(message)
        if pad_length < 0:
            raise ValueError("Message exceeds packet size")
        payload = message + ("." * pad_length)
        
        try:
            # Send the payload
            rfm9x.send(bytes(payload, "utf-8"))
            sent_packets += 1
            
            # Wait for the echo response
            response = rfm9x.receive(timeout=TIMEOUT)
            if response is not None:
                try:
                    response_text = response.decode("utf-8")
                    parts = response_text.split("|")
                    # The base station echoes the message exactly, so we check for the "ping" prefix
                    if len(parts) >= 2 and parts[0] == "ping":
                        sent_timestamp = float(parts[1])
                        rtt = time.monotonic() - sent_timestamp
                        total_latency += rtt
                        received_packets += 1
                        print(f"[OK] RTT: {rtt:.3f}s | Size: {PACKET_SIZES[packet_size_index]} bytes")
                    else:
                        print(f"[WARN] Unexpected response: {response_text}")
                except Exception as e:
                    print(f"[ERROR] Failed to decode response: {e}")
            else:
                print("[DROP] No response received.")
                dropped_packets += 1
        except Exception as e:
            print(f"[ERROR] Failed to send: {e}")
            dropped_packets += 1
        
        time.sleep(PING_INTERVAL)
    
    # Final test report
    print("\n--- LoRa Network Test Report ---")
    print(f"Test duration: {TEST_DURATION} seconds")
    print(f"Packet size: {PACKET_SIZES[packet_size_index]} bytes")
    print(f"Sent: {sent_packets}")
    print(f"Received: {received_packets}")
    print(f"Dropped: {dropped_packets}")
    
    if received_packets > 0:
        avg_latency = total_latency / received_packets
        throughput = (PACKET_SIZES[packet_size_index] * received_packets * 8) / TEST_DURATION / 1000
        print(f"Average RTT: {avg_latency:.3f} seconds")
        print(f"Throughput: {throughput:.2f} kbps")
    else:
        print("No packets received — check your connection or base station.")
