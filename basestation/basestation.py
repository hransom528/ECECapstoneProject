import time
from lora_setup import get_lora_radio

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

            message = raw_input_str.encode('utf-8')
            retries = 0

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
                        print(f"[RECEIVED] {decoded}")
                        last_packet_time = time.time()
                        received_any = True
                    except UnicodeDecodeError:
                        print("[ERROR] Received invalid UTF-8 data")
                else:
                    # No packet received — check if we’ve already received some and waited enough
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
