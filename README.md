# ECECapstoneProject
ECE SP-53 Capstone Project Scripts/Code

## Summary of Files
- **basestation:** Code for the Adafruit Feather LoRA microcontroller that is connected to a laptop
- **esp32:** Arduino code for the ESP32 module that is used to create a vulnerable Wi-Fi network for testing and demoing
- **motor-control:** Motor control code for the rover, runs on the Raspberry Pi
- **old_LoRA_code:** Original testing code for the LoRA communication system (archived)
- **rover_code:** LoRA code for the rover, runs on the Raspberry Pi

## Connecting the LoRA transceiver to the Raspberry Pi

VIN: Connect to the Pi’s 3.3 V pin.

GND: Connect to any ground (GND) pin on the Pi.

SCK: Connect to the Pi’s SCLK (GPIO11, physical pin 23).

MISO: Connect to the Pi’s MISO (GPIO9, physical pin 21).

MOSI: Connect to the Pi’s MOSI (GPIO10, physical pin 19).

CS: Connect to GPIO7 (physical pin 26).

RESET: Connect to GPIO25 (physical pin 22).
