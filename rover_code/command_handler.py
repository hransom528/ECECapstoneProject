import os
import time
from datetime import datetime
from network_tests import ping_host, check_dns, check_internet_connectivity
from motor_controller import move_forward, move_backward, turn_left, turn_right, stop

MAX_HISTORY = 500  # Number of sent packets to retain in memory

# Base command class
class Command:
    name = None  # Should be overridden in subclass

    def execute(self, args, handler):
        raise NotImplementedError("Command must implement execute()")

class MoveCommand(Command):
    name = "MOVE"

    def execute(self, args, handler):
        if len(args) != 2:
            handler.send_response("Usage: MOVE <DIRECTION> <DURATION>")
            return

        direction = args[0].upper()
        try:
            duration = float(args[1])
        except ValueError:
            handler.send_response("Invalid duration. Provide a number.")
            return

        response = ""
        if direction == "FORWARD":
            move_forward()
            response = f"→ Moving forward for {duration} seconds"
        elif direction == "BACKWARD":
            move_backward()
            response = f"→ Moving backward for {duration} seconds"
        elif direction == "LEFT":
            turn_left()
            response = f"→ Turning left for {duration} seconds"
        elif direction == "RIGHT":
            turn_right()
            response = f"→ Turning right for {duration} seconds"
        elif direction == "STOP":
            stop()
            response = "→ Stopping motors"
        else:
            stop()
            response = f"→ Unknown direction: {direction}"

        handler.send_response(response)

        if direction in ["FORWARD", "BACKWARD", "LEFT", "RIGHT"]:
            time.sleep(duration)
            stop()


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


class CommandHandler:
    def __init__(self, rfm9x):
        self.rfm9x = rfm9x
        self.packet_history = []
        self.max_packet_size = 128
        self.logging_enabled = True
        self.timestamp_enabled = True
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
        ])

    def register_commands(self, command_list):
        for command in command_list:
            self.commands[command.name] = command

    def send_response(self, response, rfm9x=None):
        rfm9x = rfm9x or self.rfm9x
        encoded_response = response.encode('utf-8')

        # Determine if we’re prefixing at all
        prefix_len = 0
        if self.logging_enabled and self.timestamp_enabled:
            prefix_len = 30

        max_data_len = self.max_packet_size - prefix_len

        # Determine chunking behavior
        if self.chunking_enabled:
            chunks = [
                encoded_response[i:i + max_data_len]
                for i in range(0, len(encoded_response), max_data_len)
            ]
        else:
            chunks = [encoded_response]  # No chunking

        total = len(chunks)

        for idx, chunk in enumerate(chunks, start=1):
            if self.logging_enabled:
                if self.timestamp_enabled:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    prefix = f"[{timestamp} {idx}/{total}] "
                else:
                    prefix = f"[{idx}/{total}] "
                payload = prefix.encode('utf-8') + chunk
            else:
                payload = chunk  # No prefix at all

            rfm9x.send(payload)
            self.packet_history.append(payload)

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
