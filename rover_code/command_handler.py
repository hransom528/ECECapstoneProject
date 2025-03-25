import os

VALID_COMMANDS = {"MOVE", "LED", "STATUS", "SCAN", "STOP", "PING", "DNS", "NET", "HELP"}

def is_valid_command(command):
    return command.upper() in VALID_COMMANDS

def handle_command(command, args, rfm9x):
    try:
        command = command.upper()

        if command == "MOVE":
            direction = args[0].upper() if len(args) > 0 else "UNKNOWN"
            distance = int(args[1]) if len(args) > 1 else 0
            response = f"→ Moving {direction} for {distance} units"
            print(response)
            rfm9x.send(bytes(response, "utf-8"))
            return

        elif command == "LED":
            state = args[0].upper() if len(args) > 0 else "OFF"
            response = f"→ Turning LED {state}"
            print(response)
            rfm9x.send(bytes(response, "utf-8"))
            return

        elif command == "STATUS":
            response = "→ Rover is online and ready"
            print(response)
            rfm9x.send(bytes(response, "utf-8"))
            return

        elif command == "SCAN":
            response = "→ Scanning environment..."
            print(response)
            rfm9x.send(bytes(response, "utf-8"))
            return

        elif command == "STOP":
            response = "→ Stopping all activity"
            print(response)
            rfm9x.send(bytes(response, "utf-8"))
            return

        else:
            response = f"[UNIMPLEMENTED COMMAND] {command}"
            print(response)
            rfm9x.send(bytes(response, "utf-8"))

    except Exception as e:
        print(f"[ERROR] Command handling failed: {e}")
