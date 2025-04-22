import os
import subprocess
from subprocess import STDOUT, check_output
import time
from datetime import datetime
from network_tests import ping_host, check_dns, check_internet_connectivity
from motor_controller import move_forward, move_backward, turn_left, turn_right, stop
from images import convert_image
from file_sender import send_file
import math
import zlib
from camera import capture_photo
import csv
import threading

MAX_HISTORY = 500  # Number of sent packets to retain in memory

# Base command class
class Command:
    name = None  # Should be overridden in subclass

    def execute(self, args, handler):
        raise NotImplementedError("Command must implement execute()")

class MoveCommand(Command):
    name = "MOVE"

    def execute(self, args, handler):
        if len(args) not in (2, 3):
            handler.send_response("Usage: MOVE <DIRECTION> <DURATION> <THROTTLE>")
            return

        direction = args[0].upper()
        try:
            duration = float(args[1])
            speed = float(args[2])
            raw_speed = max(1, min(10, float(args[2])))
            speed = 0.5 + (raw_speed - 1) * (0.5 / 9)
        except ValueError:
            handler.send_response("Invalid duration. Provide a number.")
            return            

        response = ""
        if direction.upper() == "FORWARD":
            move_forward(speed)
            response = f"→ Moving forward for {duration} seconds"
        elif direction.upper() == "BACKWARD":
            move_backward(speed)
            response = f"→ Moving backward for {duration} seconds"
        elif direction.upper() == "LEFT":
            turn_left(speed)
            response = f"→ Turning left for {duration} seconds"
        elif direction.upper() == "RIGHT":
            turn_right(speed)
            response = f"→ Turning right for {duration} seconds"
        elif direction.upper() == "STOP":
            stop()
            response = "→ Stopping motors"
        else:
            stop()
            response = f"→ Unknown direction: {direction}"

        handler.send_response(response)

        if direction.upper() in ["FORWARD", "BACKWARD", "LEFT", "RIGHT"]:
            time.sleep(duration)
            stop()
        handler.send_final_token()


class LedCommand(Command):
    name = "LED"

    def execute(self, args, handler):
        state = args[0].upper() if len(args) > 0 else "OFF"
        response = f"→ Turning LED {state}"
        handler.send_response(response)
        handler.send_final_token()


class StatusCommand(Command):
    name = "STATUS"

    def execute(self, args, handler):
        response = "→ Rover is online and ready"
        handler.send_response(response)
        handler.send_final_token()


class ScanCommand(Command):
    name = "SCAN"

    def execute(self, args, handler):
        response = "→ Scanning environment..."
        #scanCmd = "sudo timeout 20s airodump-ng wlan0mon"
        #result = subprocess.getoutput(scanCmd)
        #scanCmd = ["sudo", "timeout", "20s", "airodump-ng", "wlan0mon"]
        #result = check_output(scanCmd, stderr=STDOUT)
        handler.send_response(response)
        #handler.send_reponse(result)
        handler.send_final_token()

class StopCommand(Command):
    name = "STOP"

    def execute(self, args, handler):
        response = "→ Stopping all activity"
        handler.send_response(response)
        handler.send_final_token()


class PingCommand(Command):
    name = "PING"

    def execute(self, args, handler):
        target = args[0] if len(args) > 0 else "8.8.8.8"
        response = ping_host(host=target)
        handler.send_response(response)
        time.sleep(0.2)
        handler.send_final_token()


class DnsCommand(Command):
    name = "DNS"

    def execute(self, args, handler):
        domain = args[0] if len(args) > 0 else "google.com"
        response = check_dns(domain=domain)
        handler.send_response(response)
        handler.send_final_token()


class NetCommand(Command):
    name = "NET"

    def execute(self, args, handler):
        response = check_internet_connectivity()
        handler.send_response(response)
        handler.send_final_token()


class HelpCommand(Command):
    name = "HELP"

    def execute(self, args, handler):
        # List available commands based on the registered ones
        available = ", ".join(handler.commands.keys())
        response = f"Valid commands: {available}"
        handler.send_response(response)
        handler.send_final_token()


class HistoryCommand(Command):
    name = "HISTORY"

    def execute(self, args, handler):
        try:
            if len(args) == 0:
                return handler.send_response("Usage: HISTORY (# of packets)", handler.rfm9x)
            count = int(args[0])
            history = handler.packet_history
            to_resend = history[-count:] if count <= len(history) else history
            handler.send_response(f"→ Resending last {len(to_resend)} packets", handler.rfm9x)
            for packet in to_resend:
                handler.rfm9x.send(packet)
            handler.send_final_token()
        except Exception as e:
            handler.send_response(f"[REQUEST ERROR] Invalid argument: {e}", handler.rfm9x)
            handler.send_final_token()

'''
class EchoCommand(Command):
    name = "ECHO"

    def execute(self, args, handler):
        try:
            if len(args) == 0:
                handler.send_response("Usage: ECHO (# of packets) (message)", handler.rfm9x)
                # Send termination token right away.
                handler.send_final_token()
                return

            times = int(args[0])
            message = args[1] if len(args) > 1 else ""
            # Send each echo packet.
            for i in range(times):
                handler.send_response(message, handler.rfm9x)
                time.sleep(0.1)
            # After all packets are sent, signal the end.
            handler.send_final_token()
        except Exception as e:
            handler.send_response(f"[REQUEST ERROR] Invalid argument: {e}", handler.rfm9x)
            handler.send_final_token()
'''

class EchoCommand(Command):
    name = "ECHO"

    def execute(self, args, handler):
        try:
            if len(args) == 0:
                handler.send_response("Usage: ECHO (# of packets) (message)", handler.rfm9x)
                handler.send_final_token()
                return

            times = int(args[0])
            message = args[1] if len(args) > 1 else ""

            total_bytes_sent = 0
            start_time = time.time()

            for i in range(times):
                bytes_sent = handler.send_response(message, handler.rfm9x)
                total_bytes_sent += bytes_sent
                time.sleep(0.1)  # simulate delay between packets

            end_time = time.time()
            elapsed_time = end_time - start_time

            # Calculate throughput (bytes per second)
            throughput = total_bytes_sent / elapsed_time if elapsed_time > 0 else 0
            latency_per_packet = elapsed_time / times if times > 0 else 0

            handler.send_response(f"[THROUGHPUT] {throughput:.2f} bytes/sec | [LATENCY] {latency_per_packet:.4f} sec/packet", handler.rfm9x)
            time.sleep(0.1)
            handler.send_final_token()
        except Exception as e:
            handler.send_response(f"[REQUEST ERROR] Invalid argument: {e}", handler.rfm9x)
            time.sleep(0.1)
            handler.send_final_token()


class ConfigCommand(Command):
    name = "CONFIG"

    def execute(self, args, handler):
        try:
            if len(args) == 1 and args[0].upper() == "HELP":
                response = (
                    "CONFIG OPTIONS:\n"
                    "- OUTPUT_LENGTH <32-252>\n"
                    "- LOGGING <true|false>\n"
                    "- TIMESTAMP <true|false>\n"
                    "- CHUNKING <true|false>"
                )
            elif len(args) < 2:
                raise ValueError("Usage: CONFIG <PARAM> <VALUE>")

            else:
                param, value = args[0].upper(), args[1].lower()

                if param == "OUTPUT_LENGTH":
                    new_size = int(value)
                    if 32 <= new_size <= 252:
                        handler.max_packet_size = new_size
                        response = f"Set OUTPUT_LENGTH to {new_size} bytes"
                    else:
                        response = f"Invalid OUTPUT_LENGTH: {new_size} (must be 32-252)"

                elif param == "LOGGING":
                    handler.logging_enabled = value in ["true", "1", "on"]
                    response = f"{'Enabled' if handler.logging_enabled else 'Disabled'} LOGGING"

                elif param == "TIMESTAMP":
                    handler.timestamp_enabled = value in ["true", "1", "on"]
                    response = f"{'Enabled' if handler.timestamp_enabled else 'Disabled'} TIMESTAMP"

                elif param == "CHUNKING":
                    handler.chunking_enabled = value in ["true", "1", "on"]
                    response = f"{'Enabled' if handler.chunking_enabled else 'Disabled'} CHUNKING"

                else:
                    response = f"Unknown CONFIG parameter: {param}"

        except Exception as e:
            response = f"CONFIG error: {e}"

        handler.send_response(response)
        handler.send_final_token()

class ScreenshotCommand(Command):
    name = "SCREENSHOT"
    
    def execute(self, args, handler):
        try:
            # Set image parameters – adjust as needed.
            bit_depth = 4
            size = (128, 128)
            
            # Save the original max packet size or default to 128
            original_max_packet_size = getattr(handler, "max_packet_size", 128)
            max_packet_size = original_max_packet_size

            # If a second argument is provided, try to use it as the new packet size
            if len(args) > 1:
                try:
                    max_packet_size = int(args[1])
                except ValueError:
                    handler.send_response("Invalid packet size. Must be an integer.", handler.rfm9x)
                    handler.send_final_token()
                    return

            # Temporarily override handler.max_packet_size
            handler.max_packet_size = max_packet_size

            # Determine the image path
            script_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(script_dir, "img", args[0])
            
            # Load, dither, and pack image bits (returns a bytearray)
            hex_data = convert_image(image_path, bit_depth=bit_depth, size=size, dithering=False)
            if not hex_data:
                handler.send_response("Image conversion failed", handler.rfm9x)
                return
            
            # Optionally write to terminal log
            with open("terminal.txt", "w") as f:
                f.write(hex_data)
            
            handler.send_response(f"Sending an {size} {bit_depth}bpp image in {max_packet_size}-byte chunks")

            # Send the image data
            if send_file(hex_data, handler):
                # handler.send_response("SCREENSHOT SENT", handler.rfm9x)
                handler.send_final_token()
            else:
                handler.send_response("Failed to send screenshot", handler.rfm9x)
                handler.send_final_token()

            # Restore the original packet size
            handler.max_packet_size = original_max_packet_size
            # handler.send_final_token()
                
        except Exception as e:
            # Restore even if there's an error
            handler.max_packet_size = original_max_packet_size
            handler.send_response(f"[SCREENSHOT ERROR] {e}", handler.rfm9x)
            handler.send_final_token()

class CameraCommand(Command):
    name = "CAMERA"
    
    def execute(self, args, handler):
        try:
            
            import time

            while True:
                image_path = capture_photo()
                if image_path:
                    break  
                print("Retrying capture...")
                time.sleep(1)  

            image_path = capture_photo()
            
            # Set image parameters – adjust as needed.
            bit_depth = 4
            size = (64, 64)
            
            # Load, dither, and pack image bits (returns a bytearray)
            hex_data = convert_image(image_path, bit_depth=bit_depth, size=size, dithering=False)
            if not hex_data:
                handler.send_response("Image conversion failed", handler.rfm9x)
                return
            
            with open("terminal.txt", "w") as f:
                f.write(hex_data)
            
            handler.send_response(f"Sending an {size} {bit_depth}bpp image")
            # # Send the file using file_sender's send_file function
            if send_file(hex_data, handler):
                handler.send_response("SCREENSHOT SENT", handler.rfm9x)
            else:
                handler.send_response("Failed to send screenshot", handler.rfm9x)
                
        except Exception as e:
            handler.send_response(f"[SCREENSHOT ERROR] {e}", handler.rfm9x)

class ResendCommand(Command):
    name = "RESEND"
    
    def execute(self, args, handler):
        """
        Resends specific packets based on a comma-separated list of packet sequence numbers.
        Example command: RESEND 0,2,5
        """
        if not args:
            handler.send_response("Usage: RESEND <packet numbers, comma separated>", handler.rfm9x)
            return
        try:
            # Combine all arguments into one string in case spaces are used.
            indices_str = " ".join(args).replace(":", "").strip()
            # Split by commas (and spaces) to extract packet indices.
            indices = []
            for part in indices_str.split(","):
                for token in part.split():
                    token = token.strip()
                    if token.isdigit():
                        indices.append(int(token))
            if not indices:
                handler.send_response("No valid packet indices provided for RESEND.", handler.rfm9x)
                return
            history = handler.packet_history
            for i in indices:
                try:
                    packet = history[i]
                    handler.rfm9x.send(packet)
                    print(f"Resent packet {i}")
                except IndexError:
                    handler.send_response(f"Packet {i} not found in history.", handler.rfm9x)
        except Exception as e:
            handler.send_response(f"[RESEND ERROR] {e}", handler.rfm9x)

# Bluetooth scanning subprocess
def bluetoothScanProcess():
    scanCmd = ["sudo", "hcitool", "scan", "--length", "6"]
    result = subprocess.run(scanCmd, stderr=STDOUT, stdout=subprocess.PIPE, text=True, universal_newlines=True)
    return result.stdout

# Bluetooth scanning command
class ScanBluetoothCommand(Command):
    name = "SCANBT"

    def execute(self, args, handler):
        response = "→ Scanning Bluetooth devices..."
        handler.send_response(response, handler.rfm9x)
        result = bluetoothScanProcess()
        handler.send_response(result, handler.rfm9x)
        handler.send_final_token()

class WifiSetupCommand(Command):
    name = "WIFISETUP"

    def execute(self, args, handler):
        response = "→ WiFi Set Up Successfully!"
        #checkKillCmd = ["sudo", "airmon-ng", "check", "kill"]
        #subprocess.run(checkKillCmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        monitorModeCmd = ["sudo", "airmon-ng", "start", "wlan1"]
        subprocess.run(monitorModeCmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        handler.send_response(response)
        handler.send_final_token()

class WiFiScanCommand(Command):
    name = "WIFISCAN"

    def execute(self, args, handler):
        # Run scanning command
        #response = "→ Scanning Wi-Fi devices..."
        timeoutPeriod = 30 # Timeout process after a specified period (s)
        airodumpCmd = ["sudo", "airodump-ng", "--essid", "ECE_SP25_53", "--channel", "1", "--write", "handshk", "wlan1mon"]
        subprocess.run(airodumpCmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeoutPeriod)
        
        # Open captured CSV file
        with open('handshk-01.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            for row in reader:
                handler.send_response(row)
        handler.send_final_token()

        # Cleanup scan files afterwards
        os.remove('handshk-01.cap')
        os.remove('handshk-01.csv')
        os.remove('handshk-01.kismet.csv')
        os.remove('handshk-01.kismet.netxml')
        os.remove('handshk-01.log.csv')


class CommandHandler:
    def __init__(self, rfm9x):
        self.rfm9x = rfm9x
        self.rfm9x.ack_delay = 0.01
        self.rfm9x.node = 1
        self.rfm9x.destination = 2
        self.packet_history = []
        self.max_packet_size = 224
        self.logging_enabled = False
        self.timestamp_enabled = False
        self.chunking_enabled = True
        self.commands = {}
        self.register_commands([
            MoveCommand(),
            LedCommand(),
            StatusCommand(),
            ScanCommand(),
            StopCommand(),
            PingCommand(),
            DnsCommand(),
            NetCommand(),
            HelpCommand(),
            HistoryCommand(),
            EchoCommand(),
            ConfigCommand(),
            ScreenshotCommand(),
            CameraCommand(),
            ResendCommand(),  # New RESEND command added here.
            ScanBluetoothCommand(),
            WifiSetupCommand(),
            WiFiScanCommand(),
        ])


    def register_commands(self, command_list):
        for command in command_list:
            self.commands[command.name] = command


    def send_response(self, response, rfm9x=None):
        from datetime import datetime  # just in case it's not at the top

        rfm9x = rfm9x or self.rfm9x
        encoded_response = response.encode('utf-8')

        # Determine prefix length for timestamp/logging
        prefix_len = 0
        if self.logging_enabled and self.timestamp_enabled:
            prefix_len = 30

        max_data_len = self.max_packet_size - prefix_len

        # Chunk the response
        if self.chunking_enabled:
            chunks = [
                encoded_response[i:i + max_data_len]
                for i in range(0, len(encoded_response), max_data_len)
            ]
        else:
            chunks = [encoded_response]

        total = len(chunks)
        total_bytes_sent = 0  # <--- Track actual bytes sent

        for idx, chunk in enumerate(chunks, start=1):
            if self.logging_enabled:
                if self.timestamp_enabled:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    prefix = f"[{timestamp} {idx}/{total}] "
                else:
                    prefix = f"[{idx}/{total}] "
                payload = prefix.encode('utf-8') + chunk
            else:
                payload = chunk

            print("[DEBUG] Sending payload:", payload)
            rfm9x.send_with_ack(payload)
            self.packet_history.append(payload)

            total_bytes_sent += len(payload)  # <--- Add actual payload length

            if len(self.packet_history) > MAX_HISTORY:
                self.packet_history.pop(0)

        return total_bytes_sent  # <--- Return byte count



    def handle_command(self, command, args):
        try:
            cmd = command.upper()
            if cmd in self.commands:
                self.commands[cmd].execute(args, self)
            else:
                self.send_response(f"[UNIMPLEMENTED COMMAND] {cmd}")
        except Exception as e:
            self.send_response(f"[ERROR] Command handling failed: {e}")

    def send_final_token(self, rfm9x=None):
        rfm9x = rfm9x or self.rfm9x
        FINAL_TOKEN = "END_OF_STREAM"  # Make sure this token does not appear in regular messages.
        final_packet = FINAL_TOKEN.encode('utf-8')
        print("[DEBUG] Sending final token:", final_packet)
        rfm9x.send_with_ack(final_packet)
        self.packet_history.append(final_packet)
        if len(self.packet_history) > MAX_HISTORY:
            self.packet_history.pop(0)
