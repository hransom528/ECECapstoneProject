import time
from lora_setup import get_lora_radio
from network_test import network_test
from camera import receive_photo

# --- Configuration ---
LORA_FREQ = 915.0         # MHz (set according to your region)
TX_POWER = 23             # Max transmission power
RECEIVE_TIMEOUT = 5.0     # Max wait for first response
INTER_PACKET_TIMEOUT = 0.5  # Max wait between packets (LoRa has ~0.2s delay per packet)
LOOP_SLEEP = 0.01
MAX_RETRIES = 0

def main():
    print("Basestation online. Type commands to send to the rover. Type 'exit' to quit.")
    rfm9x = get_lora_radio()

    while True:
        try:
            raw_input_str = input(">> ").strip()
            if raw_input_str.lower() in {"exit", "quit"}:
                print("Exiting basestation.")
                break

            if not raw_input_str:
                continue

            if raw_input_str.startswith("NETWORK_TEST"):
                try:
                    _, count_str = raw_input_str.split()
                    count = int(count_str)
                    network_test(rfm9x, count)
                except (ValueError, IndexError):
                    print("[ERROR] Usage: NETWORK_TEST <count>")
                continue
            
            # Handle the SCREENSHOT command by delegating to camera.receive_photo()
            if raw_input_str.startswith("SCREENSHOT"):
                print("Requesting screenshot from rover...")
                # Send the SCREENSHOT command as raw bytes so that no conversion occurs.
                rfm9x.send("SCREENSHOT".encode('utf-8'))
                # Allow a brief delay for the rover to begin transmitting.
                time.sleep(0.5)
                # Receive and reconstruct the photo via the camera module.
                receive_photo(rfm9x)
                continue

            # Normal message handling
            message = raw_input_str.encode('utf-8')
            print(f"[TX] Sending ({len(message)} bytes): {raw_input_str}")
            rfm9x.send(message)

            print(f"[RX] Waiting for response... (timeout: {RECEIVE_TIMEOUT}s)")
            start_time = time.time()
            last_packet_time = time.time()
            received_any = False

            while time.time() - start_time < RECEIVE_TIMEOUT:
                packet = rfm9x.receive(timeout=INTER_PACKET_TIMEOUT)
                if packet:
                    try:
                        decoded = packet.decode('utf-8').strip()
                        print(f"[RECEIVED] [{len(packet)} bytes]: {decoded}")
                        last_packet_time = time.time()
                        received_any = True
                    except UnicodeDecodeError:
                        print("[ERROR] Received invalid UTF-8 data")
                else:
                    if received_any and (time.time() - last_packet_time > INTER_PACKET_TIMEOUT):
                        break

        except KeyboardInterrupt:
            print("\n[CTRL+C] Exiting basestation.")
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
