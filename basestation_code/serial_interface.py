import time
import serial
import serial.tools.list_ports
import threading
from script_handler import ScriptRunner
from datetime import datetime

LOG_FILE = "log.txt"

def log_to_file(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}    {message}\n")


def find_adafruit_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        raise IOError("No serial ports found.")
    for port in ports:
        if "Adafruit" in port.description or "Feather" in port.description:
            print(f"[INFO] Found device on {port.device}: {port.description}")
            log_to_file(f"[INFO] Found device on {port.device}: {port.description}")
            return port.device
    if len(ports) == 1:
        print(f"[INFO] Only one serial port found. Using {ports[0].device}")
        log_to_file(f"[INFO] Only one serial port found. Using {ports[0].device}")
        return ports[0].device
    print("[INFO] Multiple serial ports found:")
    log_to_file("[INFO] Multiple serial ports found:")
    for i, port in enumerate(ports):
        print(f"{i}: {port.device} - {port.description}")
        log_to_file(f"{i}: {port.device} - {port.description}")
    idx = int(input("Enter the number of the port to use: "))
    return ports[idx].device


class SerialInterface:
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
        self.FILE_TRANSFER_GAP = 1.0

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            print(f"[INFO] Connected to {self.port} at {self.baudrate} baud.")
            log_to_file(f"[INFO] Connected to {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"[ERROR] Could not open serial port {self.port}: {e}")
            log_to_file(f"[ERROR] Could not open serial port {self.port}: {e}")
            raise e

    import zlib
    import re
    import png  # make sure pypng is installed

    def finish_file_transfer(self, bit_depth=4, image_size=(128, 128)):
        if not self.file_transfer_buffer:
            return

        try:
            hex_str = self.file_transfer_buffer.decode('ascii').strip()
            if not re.fullmatch(r'[0-9a-fA-F]+', hex_str):
                raise ValueError("Invalid hex data received.")

            compressed_data = bytes.fromhex(hex_str)
            decompressed = zlib.decompress(compressed_data)

            width, height = image_size
            total_pixels = width * height
            max_val = (1 << bit_depth) - 1
            scale = 255 // max_val

            pixels = []
            buffer = 0
            bits_in_buffer = 0

            for byte in decompressed:
                buffer = (buffer << 8) | byte
                bits_in_buffer += 8

                while bits_in_buffer >= bit_depth and len(pixels) < total_pixels:
                    bits_in_buffer -= bit_depth
                    val = (buffer >> bits_in_buffer) & max_val
                    pixels.append(val * scale)

                buffer &= (1 << bits_in_buffer) - 1

            image = []
            for i in range(height):
                row = pixels[i * width:(i + 1) * width]
                image.append(row)

            output_path = "reconstructed.png"
            with open(output_path, 'wb') as f:
                writer = png.Writer(width, height, greyscale=True, bitdepth=8)
                writer.write(f, image)

            print(f"[FEATHER] Image reconstruction complete. Saved to '{output_path}'")
            log_to_file(f"[FEATHER] Image reconstruction complete. Saved to '{output_path}'")

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
                else:
                    self.send_command(cmd)
        except KeyboardInterrupt:
            print("\n[INFO] Keyboard interrupt received. Exiting...")
            log_to_file("[INFO] Keyboard interrupt received. Exiting...")
        finally:
            self.close()

    def close(self):
        self.stop_event.set()
        if self.reader_thread:
            self.reader_thread.join()
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[INFO] Serial port closed.")
            log_to_file("[INFO] Serial port closed.")
