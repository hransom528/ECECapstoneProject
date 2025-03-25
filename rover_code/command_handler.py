import os
from network_tests import ping_host, check_dns, check_internet_connectivity

MAX_PACKET_SIZE = 64 # Maximum packet size sent. Leads to chunking. 

VALID_COMMANDS = {"MOVE", "LED", "STATUS", "SCAN", "STOP", "PING", "DNS", "NET", "HELP"}

def is_valid_command(command):
    return command.upper() in VALID_COMMANDS

def send_response(response, rfm9x):
    data = response.encode('utf-8')
    chunks = [data[i:i+MAX_PACKET_SIZE] for i in range(0, len(data), MAX_PACKET_SIZE)]
    for idx, chunk in enumerate(chunks):
        rfm9x.send(chunk)

def handle_command(command, args, rfm9x):
    try:
        command = command.upper()

        if command == "MOVE":
            direction = args[0].upper() if len(args) > 0 else "UNKNOWN"
            distance = int(args[1]) if len(args) > 1 else 0
            response = f"→ Moving {direction} for {distance} units"
            # print(response)
            send_response(response, rfm9x)
            return

        elif command == "LED":
            state = args[0].upper() if len(args) > 0 else "OFF"
            response = f"→ Turning LED {state}"
            # print(response)
            send_response(response, rfm9x)
            return

        elif command == "STATUS":
            response = "→ Rover is online and ready"
            # print(response)
            send_response(response, rfm9x)
            return

        elif command == "SCAN":
            response = "→ Scanning environment..."
            # print(response)
            send_response(response, rfm9x)
            return

        elif command == "STOP":
            response = "→ Stopping all activity"
            # print(response)
            send_response(response, rfm9x)
            return
        
        elif command == "PING":
            target = args[0] if len(args) > 0 else "8.8.8.8"
            response = ping_host(host=target)
            # print(response)
            send_response(response, rfm9x)
            return

        elif command == "DNS":
            domain = args[0] if len(args) > 0 else "google.com"
            response = check_dns(domain=domain)
            # print(response)
            send_response(response, rfm9x)
            return

        elif command == "NET":
            response = check_internet_connectivity()
            # print(response)
            send_response(response, rfm9x)
            return
        
        elif command == "HELP":
            response = str(VALID_COMMANDS)
            # print(response)
            send_response(response, rfm9x)

        else:
            response = f"[UNIMPLEMENTED COMMAND] {command}"
            # print(response)
            rfm9x.send(bytes(response, "utf-8"))

    except Exception as e:
        print(f"[ERROR] Command handling failed: {e}")
