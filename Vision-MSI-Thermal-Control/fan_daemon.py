#!/usr/bin/env python3

"""
Vision MSI Thermal Control
Created by Sunray_Vision
Reverse engineering of MSI Modern 15H AI C1MGT-096IT EC for Linux thermal management
"""

import time
import os
import subprocess
import sys
import re

# Assicura che config.py venga trovato
sys.path.append("/home/vincent/Vision-MSI-Thermal-Control")
import config

EC_IO_FILE = '/sys/kernel/debug/ec/ec0/io'
SYSFS_BATTERY_CAPACITY = "/sys/class/power_supply/BAT1/capacity"

# ----------------------------
# Funzioni lettura/scrittura EC
# ----------------------------

def write_ec(byte_address: int, value: int):
    try:
        with open(EC_IO_FILE, 'r+b') as f:
            f.seek(byte_address)
            f.write(bytes([value]))
        return True
    except Exception as e:
        print(f"[ERRORE] write_ec({hex(byte_address)}, {value}): {e}")
        return False

def read_ec(byte_address: int, size: int = 1):
    try:
        with open(EC_IO_FILE, 'rb') as f:
            f.seek(byte_address)
            data = f.read(size)
        return int.from_bytes(data, 'big')
    except Exception as e:
        print(f"[ERRORE] read_ec({hex(byte_address)}): {e}")
        return 0

# ----------------------------
#   Applica FAN PROFILE
# ----------------------------

def apply_fan_profile(profile_id):
    if profile_id != 4:
        write_ec(config.EC_COOLER_BOOSTER_CONTROL_ADDR, config.EC_COOLER_BOOSTER_OFF_VALUE)

    if profile_id == 1:
        curve = config.AUTO_FAN_CURVE
        write_ec(config.EC_AUTO_ADV_CONTROL_ADDR, config.EC_AUTO_VALUE)

    elif profile_id == 2:
        write_ec(config.EC_AUTO_ADV_CONTROL_ADDR, config.EC_AUTO_VALUE)
        curve = [
            [min(150, max(0, v + config.BASIC_FAN_OFFSET)) for v in config.AUTO_FAN_CURVE[0]],
            [min(150, max(0, v + config.BASIC_FAN_OFFSET)) for v in config.AUTO_FAN_CURVE[1]],
        ]

    elif profile_id == 3:
        write_ec(config.EC_AUTO_ADV_CONTROL_ADDR, config.EC_ADVANCED_VALUE)
        curve = config.ADVANCED_FAN_CURVE

    elif profile_id == 4:
        write_ec(config.EC_COOLER_BOOSTER_CONTROL_ADDR, config.EC_COOLER_BOOSTER_ON_VALUE)
        print("[DAEMON] Cooler Booster attivato.")
        return

    for i in range(2):
        for j in range(7):
            addr = config.EC_FAN_CURVE_ADDRESSES[i][j]
            val = curve[i][j]
            write_ec(addr, val)

    print(f"[DAEMON] Profilo ventole applicato: {profile_id}")

# ----------------------------
#   Applica soglia batteria
# ----------------------------

def apply_battery_threshold(threshold):
    write_ec(config.EC_BATTERY_THRESHOLD_ADDR, threshold + 128)
    time.sleep(1)
    write_ec(config.EC_BATTERY_THRESHOLD_ADDR, 128 + 100)
    time.sleep(1)
    write_ec(config.EC_BATTERY_THRESHOLD_ADDR, threshold + 128)
    print(f"[DAEMON] Soglia batteria impostata correttamente: {threshold}%")

# ----------------------------
#   Lettura INTELLIGENTE batteria (3 METODI)
# ----------------------------

def get_battery_capacity_smart():
    """Legge la batteria da multiple fonti e sceglie la migliore"""
    try:
        # Metodo 1: Sysfs (PIÙ AFFIDABILE - lo preferiamo)
        try:
            with open("/sys/class/power_supply/BAT1/capacity", "r") as f:
                sysfs_value = int(f.read().strip())
                if 1 <= sysfs_value <= 100:
                    print(f"[BATTERY] Lettura da sysfs: {sysfs_value}%")
                    return sysfs_value
                else:
                    print(f"[BATTERY] Sysfs valore non valido: {sysfs_value}%")
        except Exception as e:
            print(f"[BATTERY] Sysfs fallito: {e}")

        # Metodo 2: EC con indirizzi prioritari
        ec_addresses = [0xbf, 0xe2, 0xd7, 0xef, 0x68, 0x80]
        valid_ec_readings = []
        
        for addr in ec_addresses:
            value = read_ec(addr, 1)
            if 1 <= value <= 100:
                print(f"[BATTERY] Trovato all'indirizzo {hex(addr)}: {value}%")
                valid_ec_readings.append((addr, value))
        
        # Se abbiamo letture EC valide, scegliamo la più plausibile
        if valid_ec_readings:
            # Preferiamo valori NON 100% (potrebbero essere fissi)
            non_100_values = [(addr, val) for addr, val in valid_ec_readings if val < 95]
            if non_100_values:
                best_addr, best_value = non_100_values[0]
                print(f"[BATTERY] Scelto {hex(best_addr)}: {best_value}% (non-100)")
                return best_value
            else:
                # Se tutti sono 100%, prendi il primo
                best_addr, best_value = valid_ec_readings[0]
                print(f"[BATTERY] Scelto {hex(best_addr)}: {best_value}% (tutti 100%)")
                return best_value

        # Metodo 3: Lettura raw da /proc (fallback estremo)
        try:
            result = subprocess.run(["acpi", "-b"], capture_output=True, text=True)
            if result.returncode == 0:
                # Esempio output: "Battery 0: Charging, 45%, 01:23:45 until charged"
                match = re.search(r'(\d+)%', result.stdout)
                if match:
                    acpi_value = int(match.group(1))
                    print(f"[BATTERY] Lettura da acpi: {acpi_value}%")
                    return acpi_value
        except Exception as e:
            print(f"[BATTERY] ACPI fallito: {e}")

        # Se TUTTO fallisce
        print("[BATTERY] ERRORE: Impossibile determinare livello batteria")
        return 0
        
    except Exception as e:
        print(f"[BATTERY] ERRORE critico: {e}")
        return 0

def monitor_battery():
    """Monitora la batteria - SOLO LETTURA, NO SCRITTURA"""
    capacity = get_battery_capacity_smart()
    
    # SOLO LOGGING - non scrivere in sysfs che è readonly!
    if capacity > 0:
        print(f"[DAEMON] Livello batteria rilevato: {capacity}%")
    else:
        print(f"[DAEMON] Batteria: lettura fallita")
    
    return capacity

# ----------------------------
#   Loop principale
# ----------------------------

def main():
    print("[DAEMON] Avviato. Controllo ventole e batteria attivi.")

    apply_fan_profile(config.DEFAULT_FAN_PROFILE)
    apply_battery_threshold(config.BATTERY_CHARGE_THRESHOLD)

    battery_check_counter = 0
    
    while True:
        # Controlla batteria ogni 5 cicli (2.5 minuti) invece che ogni 30 secondi
        battery_check_counter += 1
        if battery_check_counter >= 5:
            monitor_battery()
            battery_check_counter = 0
            
        time.sleep(30)

if __name__ == "__main__":
    main()