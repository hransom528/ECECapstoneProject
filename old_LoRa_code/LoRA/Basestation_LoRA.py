import time
import board
import busio
import digitalio
import adafruit_rfm9x
import supervisor
import sys

# --- Setup SPI Interface and LoRa pins ---
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.RFM_CS)      # Chip Select pin for LoRa radio
reset = digitalio.DigitalInOut(board.RFM_RST)   # Reset pin for LoRa radio

# --- Configure the LoRa radio ---
RADIO_FREQ_MHZ = 915.0      # Frequency (915 MHz is common in the US)
BAUD_RATE = 19_200          # SPI baud rate for communication
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, RADIO_FREQ_MHZ, baudrate=BAUD_RATE)
rfm9x.tx_power = 13         # Set transmit power in dB

print("Base station ready.")
print("Type a command and press Enter to send it to the rover.")

# --- Main Loop ---
while True:
    # Check for any incoming LoRa packets (non-blocking call with a short timeout)
    packet = rfm9x.receive(timeout=0.1)
    if packet is not None:
        # Attempt to decode the received bytes into a string
        try:
            packet_text = packet.decode("utf-8")
        except Exception as e:
            packet_text = packet  # fallback if decoding fails
        print("Received packet:", packet_text)
    
    # Check if there are any bytes available from the USB serial (laptop input)
    if supervisor.runtime.serial_bytes_available:
        # Read the input line (this call will not block since we already checked)
        command = sys.stdin.readline().strip()
        if command:
            print("Sending command:", command)
            # Convert the command string into bytes and send it via LoRa
            rfm9x.send(bytes(command, "utf-8"))
    
    # Small delay to prevent hogging the processor
    time.sleep(0.1)