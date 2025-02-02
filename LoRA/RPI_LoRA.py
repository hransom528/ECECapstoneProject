# LoRA Transceiver Code for Raspberry Pi
# See: https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/circuitpython-for-rfm9x-lora

# Imports
import board
import busio
import digitalio
import adafruit_rfm9x

# Setup SPI interface
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D5)
reset = digitalio.DigitalInOut(board.D6)

# Setup radio connection over SPI
# Note that the radio is configured in LoRa mode so you can't control sync
# word, encryption, frequency deviation, or other settings!
RADIO_FREQ_MHZ = 915.0
BAUD_RATE = 19_200
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, RADIO_FREQ_MHZ, baudrate=BAUD_RATE)
rfm9x.tx_power = 13 # dB

# Function to send a packet over LoRA
def send_packet():
	pass

def receive_packet():
	pass

