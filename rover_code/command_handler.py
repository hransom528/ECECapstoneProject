import os
from datetime import datetime
from network_tests import ping_host, check_dns, check_internet_connectivity

MAX_PACKET_SIZE = 128  # Maximum LoRa packet size
MAX_HISTORY = 50       # Number of sent packets to retain in memory

VALID_COMMANDS = {
    "MOVE", "LED", "STATUS", "SCAN", "STOP", "PING", "DNS", "NET", "HELP", "REQUEST", "OUTPUT_LENGTH"
}

# In-memory buffer to store sent packets
packet_history = []

def is_valid_command(command):
    return command.upper() in VALID_COMMANDS

def send_response(response, rfm9x):
    timestamp = datetime.now().strftime("%H:%M:%S")
    encoded_response = response.encode('utf-8')

    max_data_len = MAX_PACKET_SIZE - 30
    chunks = [encoded_response[i:i+max_data_len] for i in range(0, len(encoded_response), max_data_len)]
    total = len(chunks)

    for idx, chunk in enumerate(chunks, start=1):
        prefix = f"[{timestamp} {idx}/{total}] "
        payload = prefix.encode('utf-8') + chunk

        # Send and store the payload in history
        rfm9x.send(payload)
        packet_history.append(payload)

        # Keep only last MAX_HISTORY items
        if len(packet_history) > MAX_HISTORY:
            packet_history.pop(0)

def handle_command(command, args, rfm9x):
    try:
        command = command.upper()

        if command == "MOVE":
            direction = args[0].upper() if len(args) > 0 else "UNKNOWN"
            distance = int(args[1]) if len(args) > 1 else 0
            response = f"→ Moving {direction} for {distance} units"
            send_response(response, rfm9x)
            return

        elif command == "LED":
            state = args[0].upper() if len(args) > 0 else "OFF"
            response = f"→ Turning LED {state}"
            send_response(response, rfm9x)
            return

        elif command == "STATUS":
            response = "→ Rover is online and ready"
            send_response(response, rfm9x)
            return

        elif command == "SCAN":
            response = "→ Scanning environment..."
            send_response(response, rfm9x)
            return

        elif command == "STOP":
            response = "→ Stopping all activity"
            send_response(response, rfm9x)
            return

        elif command == "PING":
            target = args[0] if len(args) > 0 else "8.8.8.8"
            response = ping_host(host=target)
            send_response(response, rfm9x)
            return

        elif command == "DNS":
            domain = args[0] if len(args) > 0 else "google.com"
            response = check_dns(domain=domain)
            send_response(response, rfm9x)
            return

        elif command == "NET":
            response = check_internet_connectivity()
            send_response(response, rfm9x)
            return

        elif command == "HELP":
            response = str(VALID_COMMANDS)
            send_response(response, rfm9x)
            return

        elif command == "REQUEST":
            try:
                count = int(args[0]) if len(args) > 0 else 1
                to_resend = packet_history[-count:] if count <= len(packet_history) else packet_history
                send_response(f"→ Resending last {len(to_resend)} packets", rfm9x)
                for packet in to_resend:
                    rfm9x.send(packet)
            except Exception as e:
                error_msg = f"[REQUEST ERROR] Invalid argument: {e}"
                send_response(error_msg, rfm9x)
            return

        elif command == "OUTPUT_LENGTH":
            try:
                if len(args) == 0:
                    raise ValueError("No value provided.")

                new_size = int(args[0])
                if 32 <= new_size <= 200:
                    global MAX_PACKET_SIZE 
                    MAX_PACKET_SIZE = new_size
                    response = f"Updated output packet length to {new_size} bytes"
                else:
                    response = f"Invalid size: {new_size} (must be between 1 and 200)"
            except Exception as e:
                response = f"Failed to update packet length: {e}"
            send_response(response, rfm9x)
    
        else:
            response = f"[UNIMPLEMENTED COMMAND] {command}"
            send_response(response, rfm9x)

    except Exception as e:
        send_response(f"[ERROR] Command handling failed: {e}", rfm9x)
