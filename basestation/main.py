from network_test import run_network_test
from unspecified_test import run_unspecified_test

def main_menu():
    while True:
        print("\n--- RPI LoRa CLI ---")
        print("1) Network Test (Latency & Throughput)")
        print("2) Unspecified Test")
        print("q) Quit")
        choice = input("Enter your choice: ").strip().lower()
        
        if choice in ['q', 'quit']:
            print("Exiting RPI LoRa CLI.")
            break
        elif choice == '1':
            run_network_test()
        elif choice == '2':
            run_unspecified_test()
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main_menu()
