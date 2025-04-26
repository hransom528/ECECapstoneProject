import os
import time

class ScriptRunner:
    """
    Runs command scripts located in the specified scripts directory.
    Supports commands, WAIT delays, FOR loops, and ignores comments (#).
    """
import os

def __init__(self, command_handler, scripts_dir=None):
    if scripts_dir is None:
        # Get the absolute path to this script's directory
        base_dir = os.path.dirname(os.path.abspath(__file__))
        # Navigate to the ECECapstoneProject root if necessary
        while not os.path.isdir(os.path.join(base_dir, 'scripts')) and base_dir != '/':
            base_dir = os.path.dirname(base_dir)
        scripts_dir = os.path.join(base_dir, 'scripts')
    
    self.command_handler = command_handler
    self.scripts_dir = scripts_dir


    def run_script(self, filename):
        full_path = os.path.join(self.scripts_dir, filename)
        print(f"[SCRIPT] Running command script: {full_path}")
        try:
            with open(full_path, "r") as f:
                # Remove empty lines and comments
                lines = []
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "#" in line:
                        line = line.split("#", 1)[0].strip()
                    if line:
                        lines.append(line)
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
            elif line.upper().startswith("WAIT"):
                self._handle_wait(line)
                i += 1
            else:
                print(f"[SCRIPT] >> {line}")
                self.command_handler(line)
                i += 1

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
                line = block[j]
                if line.upper().startswith("WAIT"):
                    self._handle_wait(line)
                else:
                    print(f"[SCRIPT] >> {line}")
                    self.command_handler(line)
                j += 1

        return i + 1

    def _handle_wait(self, line):
        try:
            delay = float(line.split(" ", 1)[1].strip())
            print(f"[SCRIPT] Waiting {delay} seconds...")
            time.sleep(delay)
        except (IndexError, ValueError):
            print(f"[SCRIPT] Invalid WAIT syntax: {line}")
