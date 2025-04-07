import os
import time

def parse_delay(delay_str):
    try:
        return int(delay_str)
    except ValueError:
        return None

class ScriptRunner:
    """
    Runs command scripts located in the specified scripts directory.
    Supports commands, optional delays, and FOR loops.
    """
    def __init__(self, command_handler, scripts_dir="./scripts"):
        self.command_handler = command_handler
        self.scripts_dir = scripts_dir

    def run_script(self, filename):
        full_path = os.path.join(self.scripts_dir, filename)
        print(f"[SCRIPT] Running command script: {full_path}")
        try:
            with open(full_path, "r") as f:
                # Remove empty lines and comments
                lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        except FileNotFoundError:
            print(f"[ERROR] Script file '{filename}' not found in {self.scripts_dir}")
            return
        except Exception as e:
            print(f"[ERROR] Problem reading script file: {e}")
            return

        self._process_lines(lines)

    def _process_lines(self, lines):
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.upper().startswith("FOR:"):
                i = self._process_for_loop(lines, i)
            else:
                # Execute command
                print(f"[SCRIPT] >> {line}")
                self.command_handler(line)
                i += 1
                # Check if the next line is a valid delay.
                if i < len(lines):
                    delay = parse_delay(lines[i])
                    if delay is not None:
                        print(f"[SCRIPT] Waiting {delay} seconds...")
                        time.sleep(delay)
                        i += 1  # Consume the delay line only if it's valid.

    def _process_for_loop(self, lines, start_index):
        try:
            repeat_count = int(lines[start_index].split(":", 1)[1].strip())
        except ValueError:
            print(f"[SCRIPT] Invalid FOR syntax: {lines[start_index]}")
            return start_index + 1

        block = []
        i = start_index + 1
        while i < len(lines) and lines[i].upper() != "END":
            block.append(lines[i])
            i += 1

        if i == len(lines):
            print("[SCRIPT] ERROR: Missing END for FOR loop")
            return i

        for _ in range(repeat_count):
            j = 0
            while j < len(block):
                cmd = block[j]
                print(f"[SCRIPT] >> {cmd}")
                self.command_handler(cmd)
                j += 1
                # Check for optional delay within the loop.
                if j < len(block):
                    delay = parse_delay(block[j])
                    if delay is not None:
                        print(f"[SCRIPT] Waiting {delay} seconds...")
                        time.sleep(delay)
                        j += 1
        return i + 1
