import time
import board
import busio
import digitalio
import adafruit_rfm9x

'''
The purpose of this module is to echo packets back, just as they were received. 
'''

# --- Configuration Parameters ---
RECEIVE_TIMEOUT = 2.0   # Timeout (seconds) for rfm9x.receive() to wait for a packet
LOOP_SLEEP = 0.001        # Sleep duration (seconds) in main loop to yield CPU control

# --- Setup SPI Interface and LoRa pins ---
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.CE1)
reset = digitalio.DigitalInOut(board.D25)

# --- Configure the LoRa radio ---
RADIO_FREQ_MHZ = 915.0      # Frequency (915 MHz is common in the US)
BAUD_RATE = 19_200          # SPI baud rate for communication
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, RADIO_FREQ_MHZ, baudrate=BAUD_RATE)
rfm9x.tx_power = 13         # Set transmit power in dB

print("Base station ready. Echoing packets...")

# --- Main Loop ---
while True:
    packet = rfm9x.receive(timeout=RECEIVE_TIMEOUT)
    if packet is not None:
        # Debug: show raw bytes
        rfm9x.send(packet)
        print("Received packet (raw bytes):", packet)
        # Echo the packet back exactly as received
        print("Echoed packet back.")
    time.sleep(LOOP_SLEEP)