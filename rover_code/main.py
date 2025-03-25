import time
import board
import busio
import digitalio
import adafruit_rfm9x
from lora_setup import get_lora_radio
from command_handler import handle_command

'''
The purpose of this module is to communicate with the basestation. This is what should be running at all times on the rover. 
'''

# --- Configuration Parameters ---
RECEIVE_TIMEOUT = 2.0   # Timeout (seconds) for rfm9x.receive() to wait for a packet
LOOP_SLEEP = 0.001        # Sleep duration (seconds) in main loop to yield CPU control

rfm9x = get_lora_radio()

print("LoRa transceiver is initialized. Ready to receive commands!")

# --- Main Loop ---
while True:
    packet = rfm9x.receive(timeout=RECEIVE_TIMEOUT)
    if packet:
        try:
            message = packet.decode("utf-8")
            print(f"[RECEIVED] {message}")
            handle_command(message)
        except Exception as e:
            print(f"[ERROR] Packet processing failed: {e}")
    time.sleep(LOOP_SLEEP)