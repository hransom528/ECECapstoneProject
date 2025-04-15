import time
import serial
import threading
from script_handler import ScriptRunner
from reconstructor import convert_terminal_to_image

from logger import log_to_file
from .port_finder import find_adafruit_port
from .file_transfer import reconstruct_image_from_hex


class SerialInterface:
    FILE_TRANSFER_GAP = 1.0  # seconds

    def __init__(self, port=None, baudrate=115200, timeout=1):
        self.port = port if port is not None else find_adafruit_port()
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.stop_event = threading.Event()
        self.reader_thread = None
        self.file_transfer_active = False
        self.file_transfer_buffer = bytearray()
        self.file_transfer_last_time = None

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"[INFO] Connected to {self.port} at {self.baudrate} baud.")
            log_to_file(f"[INFO] Connected to {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"[ERROR] Could not open serial port {self.port}: {e}")
            log_to_file(f"[ERROR] Could not open serial port {self.port}: {e}")
            raise e

    def finish_file_transfer(self, bit_depth=4, image_size=(128, 128)):
        if not self.file_transfer_buffer:
            return

        try:
            hex_str = self.file_transfer_buffer.decode('ascii').strip()
            reconstruct_image_from_hex(hex_str, output_path="reconstructed.png",
                                       bit_depth=bit_depth, image_size=image_size)
        except Exception as e:
            print(f"[ERROR] Failed to reconstruct image: {e}")
            log_to_file(f"[ERROR] Failed to reconstruct image: {e}")

        self.file_transfer_active = False
        self.file_transfer_buffer = bytearray()
        self.file_transfer_last_time = None

    def start_reader(self):
        def read_from_port():
            buffer = b""
            while not self.stop_event.is_set():
                try:
                    if self.ser.in_waiting > 0:
                        data = self.ser.read(self.ser.in_waiting)
                        buffer += data
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        try:
                            decoded_line = line.decode('utf-8')
                            if self.file_transfer_active:
                                self.finish_file_transfer()
                            print(f"[FEATHER] {decoded_line.strip()}")
                            log_to_file(f"[FEATHER] {decoded_line.strip()}")
                        except UnicodeDecodeError:
                            if not self.file_transfer_active:
                                print("[FEATHER] Entering file transfer mode (raw binary detected).")
                                log_to_file("[FEATHER] Entering file transfer mode (raw binary detected).")
                                self.file_transfer_active = True
                            self.file_transfer_buffer.extend(line)
                            self.file_transfer_last_time = time.time()
                    if self.file_transfer_active:
                        if self.file_transfer_last_time and (time.time() - self.file_transfer_last_time > self.FILE_TRANSFER_GAP):
                            if buffer:
                                self.file_transfer_buffer.extend(buffer)
                                buffer = b""
                            self.finish_file_transfer()
                    else:
                        time.sleep(0.05)
                except Exception as e:
                    print(f"[ERROR] Serial read error: {e}")
                    log_to_file(f"[ERROR] Serial read error: {e}")
                    break

        self.reader_thread = threading.Thread(target=read_from_port, daemon=True)
        self.reader_thread.start()

    def send_command(self, cmd):
        if self.ser and self.ser.is_open:
            print(f"[SEND] {cmd}")
            log_to_file(f"[SEND] {cmd}")
            self.ser.write((cmd + "\r\n").encode('utf-8'))
            self.ser.flush()
        else:
            print("[ERROR] Serial port is not open.")
            log_to_file("[ERROR] Serial port is not open.")

    def interactive_mode(self):
        print(">> Type commands to send to the Feather (type 'exit' to quit):")
        try:
            while True:
                cmd = input(">> ").strip()
                if cmd.lower() in {'exit', 'quit'}:
                    print("[INFO] Exiting interactive mode...")
                    log_to_file("[INFO] Exiting interactive mode...")
                    break

                if cmd.upper().startswith("SCRIPT"):
                    parts = cmd.split()
                    if len(parts) >= 2:
                        filename = parts[1]
                        script_runner = ScriptRunner(self.send_command)
                        script_runner.run_script(filename)
                    else:
                        print("[ERROR] SCRIPT command requires a filename.")
                        log_to_file("[ERROR] SCRIPT command requires a filename.")

                elif cmd.upper().startswith("DISPLAY"):
                    self.extract_and_display_image()

                else:
                    self.send_command(cmd)
        except KeyboardInterrupt:
            print("\n[INFO] Keyboard interrupt received. Exiting...")
            log_to_file("[INFO] Keyboard interrupt received. Exiting...")
        finally:
            self.close()

    def extract_and_display_image(self):
        from config import LOG_FILE

        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

            start_idx = None
            end_idx = None

            for i in reversed(range(len(lines))):
                if "[RX] Final packet received" in lines[i]:
                    end_idx = i
                elif "[SEND] SCREENSHOT" in lines[i] and end_idx is not None:
                    start_idx = i
                    break

            if start_idx is not None and end_idx is not None:
                relevant = []
                for line in lines[start_idx:end_idx + 1]:
                    line_content = line.strip().split("    ", 1)
                    if len(line_content) == 2:
                        content = line_content[1]
                        if "[FEATHER] [RECEIVED]" in content and ": " in content:
                            payload = content.split(": ", 1)[1].strip()
                            if "[" not in payload and "]" not in payload:
                                relevant.append(payload + "\n")

                if relevant:
                    with open("terminal1.txt", "w", encoding="utf-8") as out:
                        out.writelines(relevant)

                    print("[INFO] Saved image data to terminal1.txt")
                    log_to_file("[INFO] DISPLAY extracted pure image data to terminal1.txt")

                    convert_terminal_to_image(
                        terminal_file='terminal1.txt',
                        output_path='reconstructed.png',
                        bit_depth=4,
                        size=(64, 64)
                    )

                    print("[INFO] Image reconstruction complete.")
                    log_to_file("[INFO] DISPLAY completed image reconstruction.")
                else:
                    print("[ERROR] No valid image data found in block.")
                    log_to_file("[ERROR] DISPLAY found no valid image data.")
            else:
                print("[ERROR] Could not find SCREENSHOT session in log.")
                log_to_file("[ERROR] DISPLAY could not find SCREENSHOT session.")

        except Exception as e:
            print(f"[ERROR] DISPLAY command failed: {e}")
            log_to_file(f"[ERROR] DISPLAY command failed: {e}")

    def close(self):
        self.stop_event.set()
        if self.reader_thread:
            self.reader_thread.join()
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[INFO] Serial port closed.")
            log_to_file("[INFO] Serial port closed.")
