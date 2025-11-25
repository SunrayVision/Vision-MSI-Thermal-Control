#!/usr/bin/env python3
import sys
sys.path.append("/home/vincent/OpenFreezeCenter_OG")
import config

EC_IO_FILE = '/sys/kernel/debug/ec/ec0/io'

def read_ec(byte_address: int, size: int = 1):
    try:
        with open(EC_IO_FILE, 'rb') as f:
            f.seek(byte_address)
            data = f.read(size)
        return int.from_bytes(data, 'big')
    except Exception as e:
        print(f"ERRORE read_ec({hex(byte_address)}): {e}")
        return 0

def find_battery_address():
    print("Scansionando indirizzi EC per trovare la batteria...")
    for addr in range(0x00, 0xFF):
        value = read_ec(addr, 1)
        if 1 <= value <= 100:  # Percentuali valide di batteria
            print(f"Trovato: Indirizzo {hex(addr)} = {value}%")
    
    # Controlla anche gli indirizzi noti
    print("\nControllo indirizzi noti:")
    known_addresses = [0xe2, 0xbf, 0xd7, 0xef]
    for addr in known_addresses:
        value = read_ec(addr, 1)
        print(f"Indirizzo {hex(addr)} = {value}%")

if __name__ == "__main__":
    find_battery_address()