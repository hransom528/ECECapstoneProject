import time
import board
import busio
import digitalio
import adafruit_rfm9x

# --- LoRa Setup ---
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.CE1)
reset = digitalio.DigitalInOut(board.D25)

RADIO_FREQ_MHZ = 915.0
BAUD_RATE = 19_200
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, RADIO_FREQ_MHZ, baudrate=BAUD_RATE)
rfm9x.tx_power = 13

print("Rover LoRa transceiver is ready for network testing.")

# --- Configurable Parameters ---
PACKET_SIZES = [64, 128]   # Valid packet sizes in bytes
packet_size_index = 0      # Start with first packet size
TEST_DURATION = 30         # Seconds to run the test
PING_INTERVAL = 0.5        # Time between pings (sec)
TIMEOUT = 2.0              # Timeout waiting for response

# --- Statistics ---
sent_packets = 0
received_packets = 0
total_latency = 0.0
dropped_packets = 0

# --- Begin Network Test ---
print(f"Starting LoRa test with packet size {PACKET_SIZES[packet_size_index]} bytes")
start_time = time.monotonic()

while time.monotonic() - start_time < TEST_DURATION:
    # Generate payload of desired size with timestamp
    timestamp = time.monotonic()
    message = f"ping|{timestamp}"
    pad_length = PACKET_SIZES[packet_size_index] - len(message)
    if pad_length < 0:
        raise ValueError("Message exceeds packet size")
    payload = message + ("." * pad_length)

    try:
        rfm9x.send(bytes(payload, "utf-8"))
        sent_packets += 1
        # Wait for response
        response = rfm9x.receive(timeout=TIMEOUT)
        if response is not None:
            try:
                response_text = response.decode("utf-8")
                parts = response_text.split("|")
                if len(parts) >= 2 and parts[0] == "pong":
                    sent_ts = float(parts[1])
                    rtt = time.monotonic() - sent_ts
                    total_latency += rtt
                    received_packets += 1
                    print(f"[OK] RTT: {rtt:.3f}s | Size: {PACKET_SIZES[packet_size_index]}")
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

# --- Final Report ---
print("\n--- LoRa Network Test Report ---")
print(f"Test duration: {TEST_DURATION} sec")
print(f"Packet size: {PACKET_SIZES[packet_size_index]} bytes")
print(f"Sent: {sent_packets}")
print(f"Received: {received_packets}")
print(f"Dropped: {dropped_packets}")
if received_packets:
    avg_latency = total_latency / received_packets
    print(f"Average RTT: {avg_latency:.3f} seconds")
    throughput = (PACKET_SIZES[packet_size_index] * received_packets * 8) / TEST_DURATION / 1000
    print(f"Throughput: {throughput:.2f} kbps")
else:
    print("No packets received — check your connection or base station.")

