import time
from lora_setup import get_lora_radio
import os

# --- Configuration ---
LORA_FREQ = 915.0
TX_POWER = 23
RECEIVE_TIMEOUT = 5.0
INTER_PACKET_TIMEOUT = 0.5
LOOP_SLEEP = 0.01
MAX_RETRIES = 0

def handle_command(rfm9x, command):
    FINAL_TOKEN = "END_OF_STREAM"  # Unique marker to denote end of transmission.

    message = command.encode('utf-8')
    print(f"[TX] Sending ({len(message)} bytes): {command}")
    rfm9x.send_with_ack(message)

    print(f"[RX] Waiting for response... (waiting for final packet signal '{FINAL_TOKEN}')")

    start_time = time.time()

    while True:
        packet = rfm9x.receive(timeout=INTER_PACKET_TIMEOUT, with_ack=True)
        current_time = time.time()

        if packet:
            try:
                decoded = packet.decode('utf-8').strip()
                # Check for the final packet marker.
                if decoded == FINAL_TOKEN:
                    print("[RX] Final packet received. End of message stream.")
                    break
                print(f"[RECEIVED] [{len(packet)} bytes]: {decoded}")
            except UnicodeDecodeError:
                print("[ERROR] Received invalid UTF-8 data")
        else:
            # Fallback timeout: in case we never receive the final token.
            if current_time - start_time > RECEIVE_TIMEOUT:
                print(f"[RX] Timeout: No packets received for {RECEIVE_TIMEOUT} seconds.")
                break



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

            if raw_input_str.startswith("SCRIPT"):
                try:
                    _, filename = raw_input_str.split()
                    run_script(filename, rfm9x)
                except ValueError:
                    print("[ERROR] Usage: SCRIPT <filename>")
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


def run_script(filename, rfm9x):
    full_path = os.path.join("scripts", filename)
    print(f"[SCRIPT] Running command script: {full_path}")
    try:
        with open(full_path, "r") as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

        i = 0
        while i < len(lines):
            line = lines[i]

            # Handle loops
            if line.startswith("FOR:"):
                try:
                    repeat_count = int(line.split(":")[1].strip())
                except:
                    print(f"[SCRIPT] Invalid FOR syntax: {line}")
                    i += 1
                    continue

                # Collect block until END
                block = []
                i += 1
                while i < len(lines) and lines[i] != "END":
                    block.append(lines[i])
                    i += 1

                if i == len(lines):
                    print("[SCRIPT] ERROR: Missing END for FOR loop")
                    break

                for _ in range(repeat_count):
                    j = 0
                    while j < len(block):
                        cmd = block[j]
                        print(f"[SCRIPT] >> {cmd}")
                        handle_command(rfm9x, cmd)
                        j += 1
                        if j < len(block):
                            try:
                                delay = int(block[j])
                                print(f"[SCRIPT] Waiting {delay} seconds...")
                                time.sleep(delay)
                            except ValueError:
                                print(f"[SCRIPT] Skipping invalid delay: {block[j]}")
                            j += 1
                i += 1  # Skip the END line
                continue

            # Normal command
            print(f"[SCRIPT] >> {line}")
            handle_command(rfm9x, line)
            i += 1

            if i < len(lines):
                try:
                    delay = int(lines[i])
                    print(f"[SCRIPT] Waiting {delay} seconds...")
                    time.sleep(delay)
                except ValueError:
                    print(f"[SCRIPT] Skipping invalid delay: {lines[i]}")
                i += 1

    except FileNotFoundError:
        print(f"[ERROR] Script file '{filename}' not found in scripts/")
    except Exception as e:
        print(f"[ERROR] Problem running script: {e}")
