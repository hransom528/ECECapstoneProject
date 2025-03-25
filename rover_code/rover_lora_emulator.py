from command_handler import handle_command, is_valid_command

"""
The purpose of this module is to test the rover command system locally
without using LoRa hardware. You can simulate commands using your keyboard.
This code is not what the rover should be running!! 
"""

class FakeLoRa:
    def send(self, data):
        print(f"[SENT] {data.decode('utf-8')}")


def main():
    print("LoRa simulation started. Type commands below (or 'exit' to quit).")

    rfm9x = FakeLoRa()
    
    while True:
        try:
            raw_input = input(">> ").strip()
            if raw_input.lower() in {"exit", "quit"}:
                print("Exiting simulation.")
                break

            if not raw_input:
                continue

            parts = raw_input.split()
            command = parts[0]
            args = parts[1:]

            if is_valid_command(command):
                handle_command(command, args, rfm9x)
            else:
                response = f"[IGNORED] Unknown command: {command}"
                print(response)
                rfm9x.send(bytes(response, "utf-8"))

        except KeyboardInterrupt:
            print("\n[CTRL+C] Exiting simulation.")
            break
        except Exception as e:
            print(f"[ERROR] Command processing failed: {e}")


if __name__ == "__main__":
    main()
