import time
import board
import busio
import digitalio
import adafruit_rfm9x

# --- Setup SPI Interface and LoRa Pins ---
# Define the SPI bus using the Raspberry Pi's SPI pins
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D5)    # Chip Select pin for the LoRa radio
reset = digitalio.DigitalInOut(board.D6) # Reset pin for the LoRa radio

# --- Configure the LoRa Radio ---
RADIO_FREQ_MHZ = 915.0  # Frequency (915 MHz is typical for the US; use 868 for some other regions)
BAUD_RATE = 19_200      # SPI baud rate for communication

# Create the RFM9x object for the LoRa transceiver
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, RADIO_FREQ_MHZ, baudrate=BAUD_RATE)
rfm9x.tx_power = 13     # Set the transmit power (dB)

print("Rover LoRa transceiver is ready.")
print("Waiting for commands...")

# --- Command Processing Function ---
def process_command(command):
    """
    Process incoming commands and return a response string.
    Extend this function to perform real actions on your rover.
    """
    if command == "ping":
        return "pong"
    elif command == "status":
        # Return a status message (replace with real sensor/diagnostic info)
        return "All systems operational"
    elif command.startswith("move"):
        # For example, 'move forward', 'move backward', etc.
        return f"Executing command: {command}"
    else:
        return f"Unknown command: {command}"

# --- Main Loop ---
while True:
    # Listen for incoming LoRa packets (non-blocking, short timeout)
    packet = rfm9x.receive(timeout=0.1)
    if packet is not None:
        try:
            # Decode the packet into a UTF-8 string and strip any extra whitespace
            command = packet.decode("utf-8").strip()
        except Exception as e:
            command = packet  # fallback if decoding fails
        print("Received command:", command)
        
        # Process the command and generate a response
        response = process_command(command)
        print("Response:", response)
        
        # Send the response back to the base station over LoRa
        rfm9x.send(bytes(response, "utf-8"))
    
    # Small delay to prevent maxing out the CPU
    time.sleep(0.1)
