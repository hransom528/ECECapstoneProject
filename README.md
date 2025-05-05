# ECECapstoneProject
**Remote Wireless Penetration Testing with LoRa-Controlled Rover**

This repository contains the full source code and documentation for our ECE SP-53 Capstone Project at Rutgers University. The project showcases a modular, unmanned wireless penetration testing system that uses LoRa communication to control a rover capable of Wi-Fi and Bluetooth security assessments in hard-to-reach or infrastructure-limited environments.

The platform supports long-range encrypted control, image capture, remote packet injection, and scripted penetration testing — all operable over a custom communication protocol optimized for high-latency, low-bandwidth conditions.

---

## 📄 Project Paper

You can read our full technical write-up here:  
➡️ [Read the PDF of our Capstone Paper](./Capstone_Paper.pdf)

This paper was submitted to academic and industry conferences including DEF CON 33 Demo Labs and the Asilomar Conference on Signals, Systems, and Computers (Track A7: Physical Layer Security & Privacy).

---

## Summary of Repository Files

- **`basestation/`** – Code for the Adafruit Feather LoRa microcontroller used for transmitting commands from the laptop.
- **`esp32/`** – Arduino code for the ESP32 module, which acts as an intentionally vulnerable Wi-Fi network for penetration testing demos.
- **`motor-control/`** – Python motor control scripts running on the Raspberry Pi to control rover movement.
- **`old_LoRA_code/`** – Archived early-stage LoRa testing scripts for reference.
- **`rover_code/`** – Core Python scripts running on the Raspberry Pi for receiving LoRa commands, executing tests, and returning results (e.g., image data or Wi-Fi scans).

---

## 🛠️ Wiring the LoRa Transceiver to the Raspberry Pi

| LoRa Pin | Raspberry Pi GPIO |
|----------|-------------------|
| VIN      | 3.3 V             |
| GND      | GND               |
| SCK      | GPIO11 (pin 23)   |
| MISO     | GPIO9 (pin 21)    |
| MOSI     | GPIO10 (pin 19)   |
| CS       | GPIO7 (pin 26)    |
| RESET    | GPIO25 (pin 22)   |

---

## 📜 License

This project is released under the [MIT License](LICENSE).

---

## 👥 Authors

Developed by students at Rutgers University — Department of Electrical & Computer Engineering. For more information, see the paper linked above.

---

