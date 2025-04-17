import time
from lora_setup import get_lora_radio
import os

# --- Configuration ---
LORA_FREQ = 915.0
TX_POWER = 23
RECEIVE_TIMEOUT = 10.0
INTER_PACKET_TIMEOUT = 0.4
LOOP_SLEEP = 0.01
MAX_RETRIES = 0

def handle_command(rfm9x, command):
    FINAL_TOKEN = "END_OF_STREAM"
    message = command.encode('utf-8')

    print(f"[TX] Sending ({len(message)} bytes): {command}")
    rfm9x.send_with_ack(message)

    print(f"[RX] Waiting for response... (waiting for final packet signal '{FINAL_TOKEN}')")

    start_time = time.time()
    last_packet_time = start_time
    packet_count = 0

    while True:
        packet = rfm9x.receive(timeout=INTER_PACKET_TIMEOUT, with_ack=True)
        current_time = time.time()

        if packet:
            packet_count += 1
            last_packet_time = current_time  # Reset the timeout window on every packet

            try:
                decoded = packet.decode('utf-8').strip()
                if decoded == FINAL_TOKEN:
                    print("[RX] Final packet received. End of message stream.")
                    break
                print(f"[RECEIVED #{packet_count}] [{len(packet)} bytes]: {decoded}")
            except UnicodeDecodeError:
                print(f"[ERROR] Received invalid UTF-8 data (packet #{packet_count})")

        else:
            # No packet arrived within INTER_PACKET_TIMEOUT
            if current_time - last_packet_time > RECEIVE_TIMEOUT:
                print(f"[RX] Timeout: No packets received for {RECEIVE_TIMEOUT} seconds.")
                break

    print(f"[RX] Total packets received (excluding final token): {packet_count}")

def main():
    print("Basestation online. Type commands to send to the rover. Type 'exit' to quit.")
    rfm9x = get_lora_radio()
    rfm9x.ack_delay = 0.01
    rfm9x.node = 2
    rfm9x.destination = 1

    while True:
        try:
            raw_input_str = input(">> ").strip()
            if raw_input_str.lower() in {"exit", "quit"}:
                print("Exiting basestation.")
                break

            if not raw_input_str:
                continue

            handle_command(rfm9x, raw_input_str)

        except KeyboardInterrupt:
            print("\n[CTRL+C] Exiting basestation.")
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
