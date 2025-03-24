import time
import board
import busio
import digitalio
import adafruit_rfm9x

# Define pins based on your Feather wiring
cs = digitalio.DigitalInOut(board.RFM_CS)
reset = digitalio.DigitalInOut(board.RFM_RST)

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)

while True:
    packet = rfm9x.receive(timeout=5.0)
    if packet is not None:
        print("Received message:", str(packet, "utf-8"))
    else:
        print("No message received")
    time.sleep(1)
