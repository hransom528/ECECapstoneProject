# lora_setup.py
import board
import busio
import digitalio
import adafruit_rfm9x

RADIO_FREQ_MHZ = 915.0
BAUD_RATE = 19200

def get_lora_radio():
    """Initialize and return the LoRa radio transceiver."""
    # Setup SPI and LoRa pins (adjust these as necessary for your wiring)
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(board.RFM_CS)    # Chip select pin for LoRa radio
    reset = digitalio.DigitalInOut(board.RFM_RST)   # Reset pin for LoRa radio
    
    # Create and configure the LoRa radio object
    rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, RADIO_FREQ_MHZ, baudrate=BAUD_RATE)
    rfm9x.tx_power = 13
    print("LoRa transceiver is initialized.")
    return rfm9x
