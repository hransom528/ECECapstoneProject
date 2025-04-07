from serial_interface import SerialInterface

def main():
    print("Basestation online. Starting serial interface...")
    serial_interface = SerialInterface()
    serial_interface.connect()
    serial_interface.start_reader()
    serial_interface.interactive_mode()

if __name__ == "__main__":
    main()
