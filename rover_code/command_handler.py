import os
from datetime import datetime
from network_tests import ping_host, check_dns, check_internet_connectivity

MAX_HISTORY = 500  # Number of sent packets to retain in memory

# Base command class
class Command:
    name = None  # Should be overridden in subclass

    def execute(self, args, handler):
        raise NotImplementedError("Command must implement execute()")

class MoveCommand(Command):
    name = "MOVE"

    def execute(self, args, handler):
        direction = args[0].upper() if len(args) > 0 else "UNKNOWN"
        distance = int(args[1]) if len(args) > 1 else 0
        response = f"→ Moving {direction} for {distance} units"
        handler.send_response(response)


class LedCommand(Command):
    name = "LED"

    def execute(self, args, handler):
        state = args[0].upper() if len(args) > 0 else "OFF"
        response = f"→ Turning LED {state}"
        handler.send_response(response)


class StatusCommand(Command):
    name = "STATUS"

    def execute(self, args, handler):
        response = "→ Rover is online and ready"
        handler.send_response(response)


class ScanCommand(Command):
    name = "SCAN"

    def execute(self, args, handler):
        response = "→ Scanning environment..."
        handler.send_response(response)


class StopCommand(Command):
    name = "STOP"

    def execute(self, args, handler):
        response = "→ Stopping all activity"
        handler.send_response(response)


class PingCommand(Command):
    name = "PING"

    def execute(self, args, handler):
        target = args[0] if len(args) > 0 else "8.8.8.8"
        response = ping_host(host=target)
        handler.send_response(response)


class DnsCommand(Command):
    name = "DNS"

    def execute(self, args, handler):
        domain = args[0] if len(args) > 0 else "google.com"
        response = check_dns(domain=domain)
        handler.send_response(response)


class NetCommand(Command):
    name = "NET"

    def execute(self, args, handler):
        response = check_internet_connectivity()
        handler.send_response(response)


class HelpCommand(Command):
    name = "HELP"

    def execute(self, args, handler):
        # List available commands based on the registered ones
        available = ", ".join(handler.commands.keys())
        response = f"Valid commands: {available}"
        handler.send_response(response)


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
        except Exception as e:
            handler.send_response(f"[REQUEST ERROR] Invalid argument: {e}", handler.rfm9x)


class EchoCommand(Command):
    name = "ECHO"

    def execute(self, args, handler):
        try:
            if len(args) == 0:
                return handler.send_response("Usage: ECHO (# of packets) (message)", handler.rfm9x)
            times = int(args[0])
            message = args[1] if len(args) > 1 else ""
            for _ in range(times):
                handler.send_response(message)
        except Exception as e:
            handler.send_response(f"[REQUEST ERROR] Invalid argument: {e}", handler.rfm9x)


class OutputLengthCommand(Command):
    name = "OUTPUT_LENGTH"

    def execute(self, args, handler):
        try:
            if len(args) == 0:
                raise ValueError("No value provided.")
            new_size = int(args[0])
            if 32 <= new_size <= 252:
                handler.max_packet_size = new_size
                response = f"Updated output packet length to {new_size} bytes"
            else:
                response = f"Invalid size: {new_size} (must be between 32 and 200)"
        except Exception as e:
            response = f"Failed to update packet length: {e}"
        handler.send_response(response)


class CommandHandler:
    def __init__(self, rfm9x):
        self.rfm9x = rfm9x
        self.packet_history = []
        self.max_packet_size = 128
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
            OutputLengthCommand(),
        ])

    def register_commands(self, command_list):
        for command in command_list:
            self.commands[command.name] = command

    def send_response(self, response, rfm9x=None):
        # Use provided rfm9x or default to self.rfm9x
        rfm9x = rfm9x or self.rfm9x
        timestamp = datetime.now().strftime("%H:%M:%S")
        encoded_response = response.encode('utf-8')
        max_data_len = self.max_packet_size - 30
        chunks = [
            encoded_response[i:i + max_data_len]
            for i in range(0, len(encoded_response), max_data_len)
        ]
        total = len(chunks)

        for idx, chunk in enumerate(chunks, start=1):
            prefix = f"[{timestamp} {idx}/{total}] "
            payload = prefix.encode('utf-8') + chunk

            # Send payload and store in history
            rfm9x.send(payload)
            self.packet_history.append(payload)

            # Ensure history does not exceed MAX_HISTORY
            if len(self.packet_history) > MAX_HISTORY:
                self.packet_history.pop(0)

    def handle_command(self, command, args):
        try:
            cmd = command.upper()
            if cmd in self.commands:
                self.commands[cmd].execute(args, self)
            else:
                self.send_response(f"[UNIMPLEMENTED COMMAND] {cmd}")
        except Exception as e:
            self.send_response(f"[ERROR] Command handling failed: {e}")
