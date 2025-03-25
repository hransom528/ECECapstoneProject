import busio
import digitalio
import board
import adafruit_rfm9x

# Setup SPI bus and LoRa pins on Raspberry Pi
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.CE1)    # Chip Select (GPIO7)
reset = digitalio.DigitalInOut(board.D25)   # Reset pin (GPIO25)

# Initialize the RFM9x module at 915 MHz (adjust frequency as needed)
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)

while True:
    message = "Hello from Pi!"
    print("Sending message:", message)
    rfm9x.send(bytes(message, "utf-8"))
    time.sleep(1)

