import serial.tools.list_ports
from logger import log_to_file

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
