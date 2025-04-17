# lora_setup.py
import board
import busio
import digitalio
import adafruit_rfm9x

RADIO_FREQ_MHZ = 915.0
BAUD_RATE = 19200

def get_lora_radio():
    """Initialize and return the Rover's LoRa radio transceiver."""
    # Setup SPI and LoRa pins
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    chip_select = digitalio.DigitalInOut(board.CE1)
    reset = digitalio.DigitalInOut(board.D25)
    
    # Create and configure the LoRa radio object
    rfm9x = adafruit_rfm9x.RFM9x(spi, chip_select, reset, RADIO_FREQ_MHZ, baudrate=BAUD_RATE)
    #rfm9x.tx_power = 13
    rfm9x.tx_power = 23
    print("LoRa transceiver is initialized.")
    return rfm9x
