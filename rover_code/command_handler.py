import os

# Load valid commands from file (once)
def load_valid_commands(path="commands.txt"):
    try:
        with open(path, "r") as f:
            return {line.strip().upper() for line in f if line.strip()}
    except Exception as e:
        print(f"[ERROR] Failed to load commands from {path}: {e}")
        return set()

VALID_COMMANDS = load_valid_commands()

def is_valid_command(command):
    return command.upper() in VALID_COMMANDS

def handle_command(command, args, rfm9x):
    try:
        command = command.upper()

        if command == "MOVE":
            direction = args[0].upper() if len(args) > 0 else "UNKNOWN"
            distance = int(args[1]) if len(args) > 1 else 0
            print(f"→ Moving {direction} for {distance} units")

        elif command == "LED":
            state = args[0].upper() if len(args) > 0 else "OFF"
            print(f"→ Turning LED {state}")

        elif command == "STATUS":
            print("→ Rover is online and ready")

        elif command == "SCAN":
            print("→ Scanning environment...")

        elif command == "STOP":
            print("→ Stopping all activity")

        else:
            print(f"[UNIMPLEMENTED COMMAND] {command}")

    except Exception as e:
        print(f"[ERROR] Command handling failed: {e}")
