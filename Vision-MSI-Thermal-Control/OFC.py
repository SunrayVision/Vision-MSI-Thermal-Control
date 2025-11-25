#!/usr/bin/env python3

"""
Vision MSI Thermal Control - GUI
Created by Sunray_Vision
GTK interface for MSI Modern 15H AI C1MGT-096IT thermal management
"""

import os
import gi
import config as old_config # Importa il modulo di configurazione aggiornato.

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

# Percorso del file di interfaccia con l'Embedded Controller (EC).
# L'accesso a questo file richiede privilegi di root.
EC_IO_FILE = '/sys/kernel/debug/ec/ec0/io'

# Variabile globale per memorizzare le temperature minime e massime di CPU e GPU.
# [CPU_MIN_TEMP, CPU_MAX_TEMP, GPU_MIN_TEMP, GPU_MAX_TEMP]
GLOBAL_MIN_MAX_TEMPS = [100, 0, 100, 0] # Inizializzati a valori che saranno facilmente superati/sottopassato.

# --- Funzioni di Interazione con l'Embedded Controller (EC) ---

def write_ec(byte_address: int, value: int):
    """
    Scrive un singolo byte (value) all'indirizzo (byte_address) specificato nell'Embedded Controller.
    Richiede privilegi di root. Gestisce errori di I/O.
    """
    try:
        # 'r+b' permette di seek e poi write, è più robusto per file speciali come /sys/kernel/debug/ec/ec0/io
        with open(EC_IO_FILE, 'r+b') as f:
            f.seek(byte_address)
            f.write(bytes([value])) # Assicura che `value` sia un singolo byte
    except FileNotFoundError:
        print(f"ERRORE: Il file EC '{EC_IO_FILE}' non trovato. Assicurati che il modulo 'ec_sys' sia caricato e di eseguire come root.")
        return False
    except PermissionError:
        print(f"ERRORE: Permesso negato per accedere a '{EC_IO_FILE}'. Eseguire l'applicazione con privilegi di root (es. sudo).")
        return False
    except Exception as e:
        print(f"ERRORE: Impossibile scrivere all'indirizzo EC {hex(byte_address)} con valore {value}: {e}")
        return False
    return True

def read_ec(byte_address: int, size: int, return_format: int):
    """
    Legge un certo numero di byte (size) dall'indirizzo (byte_address) specificato nell'Embedded Controller.
    Restituisce il valore in base al formato richiesto (return_format: 0 per intero, 1 per esadecimale stringa).
    Richiede privilegi di root. Gestisce errori di I/O.
    """
    try:
        with open(EC_IO_FILE, 'r+b') as f:
            f.seek(byte_address)
            data = f.read(size)
            if not data: # Se non vengono letti dati, potrebbe essere un problema
                print(f"AVVISO: Nessun dato letto dall'indirizzo EC {hex(byte_address)}.")
                return 0 # Ritorna un valore di default in caso di lettura fallita
    except FileNotFoundError:
        print(f"ERRORE: Il file EC '{EC_IO_FILE}' non trovato. Assicurati che il modulo 'ec_sys' sia caricato e di eseguire come root.")
        return 0
    except PermissionError:
        print(f"ERRORE: Permesso negato per accedere a '{EC_IO_FILE}'. Eseguire l'applicazione con privilegi di root (es. sudo).")
        return 0
    except Exception as e:
        print(f"ERRORE: Impossibile leggere dall'indirizzo EC {hex(byte_address)} di dimensione {size}: {e}")
        return 0 # Ritorna 0 in caso di errore di lettura

    if return_format == 0: # Restituisce intero
        return int(data.hex(), 16)
    elif return_format == 1: # Restituisce stringa esadecimale
        return data.hex()
    else:
        print(f"AVVISO: Formato di ritorno non valido per read_ec: {return_format}. Restituito intero per default.")
        return int(data.hex(), 16)

# --- Logica di Gestione dei Profili Ventola ---

def apply_fan_profile(profile_id: int):
    """
    Applica il profilo delle ventole specificato interagendo con l'EC.
    Parameters:
        profile_id (int): ID del profilo da applicare (1=Auto, 2=Basic, 3=Advanced, 4=Cooler Booster).
    """
    # Disattiva Cooler Booster all'inizio, a meno che non sia il profilo selezionato
    if profile_id != 4:
        write_ec(old_config.EC_COOLER_BOOSTER_CONTROL_ADDR, old_config.EC_COOLER_BOOSTER_OFF_VALUE)

    if profile_id == 1: # Auto
        write_ec(old_config.EC_AUTO_ADV_CONTROL_ADDR, old_config.EC_AUTO_VALUE)
        current_speeds = old_config.AUTO_FAN_CURVE
    elif profile_id == 2: # Basic (Auto con offset)
        write_ec(old_config.EC_AUTO_ADV_CONTROL_ADDR, old_config.EC_AUTO_VALUE) # Assicurati sia in modalità auto
        # Calcola le velocità per il profilo Basic applicando l'offset e clippando i valori
        current_speeds = [
            [max(0, min(150, val + old_config.BASIC_FAN_OFFSET)) for val in old_config.AUTO_FAN_CURVE[0]],
            [max(0, min(150, val + old_config.BASIC_FAN_OFFSET)) for val in old_config.AUTO_FAN_CURVE[1]]
        ]
    elif profile_id == 3: # Advanced
        write_ec(old_config.EC_AUTO_ADV_CONTROL_ADDR, old_config.EC_ADVANCED_VALUE)
        current_speeds = old_config.ADVANCED_FAN_CURVE
    elif profile_id == 4: # Cooler Booster
        # Attiva Cooler Booster e non scrive le curve individuali
        write_ec(old_config.EC_COOLER_BOOSTER_CONTROL_ADDR, old_config.EC_COOLER_BOOSTER_ON_VALUE)
        # Non c'è bisogno di scrivere le curve individuali in modalità Cooler Booster
        print("Cooler Booster attivato. Le curve delle ventole sono gestite dal firmware.")
        update_config_file_profile(profile_id) # Aggiorna la selezione anche per CB
        return
    else:
        print(f"AVVISO: Profilo ventola non valido: {profile_id}. Nessuna azione.")
        return

    # Scrive le curve delle ventole nell'EC per CPU e GPU
    for i in range(2): # 0 per CPU, 1 per GPU
        for j in range(7): # Per i 7 punti della curva
            address = old_config.EC_FAN_CURVE_ADDRESSES[i][j]
            speed = current_speeds[i][j]
            if not write_ec(address, speed):
                print(f"AVVISO: Fallita la scrittura della velocità {speed} all'indirizzo {hex(address)} per il profilo {profile_id}.")

    # Dopo aver applicato un profilo, aggiorna il valore nel file config.
    update_config_file_profile(profile_id)

def update_config_file_profile(profile_id: int):
    """
    Aggiorna la variabile DEFAULT_FAN_PROFILE nel file config.py.
    Questo è un modo basilare e si consiglia di usare un modulo di configurazione
    più robusto (es. json, configparser) per file di configurazione più complessi
    in un'applicazione più grande.
    """
    try:
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.py')
        with open(filepath, 'r') as f:
            lines = f.readlines()

        with open(filepath, 'w') as f:
            for line in lines:
                if line.strip().startswith('DEFAULT_FAN_PROFILE ='):
                    f.write(f'DEFAULT_FAN_PROFILE = {profile_id}\n')
                else:
                    f.write(line)
    except Exception as e:
        print(f"ERRORE: Impossibile aggiornare DEFAULT_FAN_PROFILE nel file config.py: {e}")

def update_config_file_battery_threshold(threshold: int):
    """
    Aggiorna la variabile BATTERY_CHARGE_THRESHOLD nel file config.py.
    """
    try:
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.py')
        with open(filepath, 'r') as f:
            lines = f.readlines()

        with open(filepath, 'w') as f:
            for line in lines:
                if line.strip().startswith('BATTERY_CHARGE_THRESHOLD ='):
                    f.write(f'BATTERY_CHARGE_THRESHOLD = {threshold}\n')
                else:
                    f.write(line)
    except Exception as e:
        print(f"ERRORE: Impossibile aggiornare BATTERY_CHARGE_THRESHOLD nel file config.py: {e}")

# --- Funzioni di Aggiornamento UI e Callbacks ---

def update_gui_values():
    """
    Aggiorna periodicamente i valori di temperatura e RPM delle ventole
    nell'interfaccia grafica. Questa funzione viene chiamata da un timer GLib.
    """
    # Legge le temperature correnti di CPU e GPU dall'EC.
    cpu_temp = read_ec(old_config.EC_TEMP_ADDRESSES[0], 1, 0)
    gpu_temp = read_ec(old_config.EC_TEMP_ADDRESSES[1], 1, 0)

    # Legge i valori per il calcolo degli RPM e gestisce la divisione per zero.
    cpu_rpm_raw = read_ec(old_config.EC_RPM_ADDRESSES[0], 2, 0)
    gpu_rpm_raw = read_ec(old_config.EC_RPM_ADDRESSES[1], 2, 0)

    # Evita ZeroDivisionError:
    cpu_rpm = old_config.FAN_RPM_CALIBRATION_CONSTANT // cpu_rpm_raw if cpu_rpm_raw else 0
    gpu_rpm = old_config.FAN_RPM_CALIBRATION_CONSTANT // gpu_rpm_raw if gpu_rpm_raw else 0

    # Aggiorna le etichette dell'interfaccia grafica.
    # Si assume che `main_window` (la finestra principale) sia globale e contenga gli attributi delle etichette.
    if hasattr(main_window, 'cpu_curr_label'): # Verifica che le etichette esistano
        main_window.cpu_curr_label.set_text(str(cpu_temp))
        main_window.gpu_curr_label.set_text(str(gpu_temp))

        # Aggiorna le temperature minime e massime registrate globalmente.
        if cpu_temp < GLOBAL_MIN_MAX_TEMPS[0]: GLOBAL_MIN_MAX_TEMPS[0] = cpu_temp
        if cpu_temp > GLOBAL_MIN_MAX_TEMPS[1]: GLOBAL_MIN_MAX_TEMPS[1] = cpu_temp
        main_window.cpu_min_label.set_text(str(GLOBAL_MIN_MAX_TEMPS[0]))
        main_window.cpu_max_label.set_text(str(GLOBAL_MIN_MAX_TEMPS[1]))

        if gpu_temp < GLOBAL_MIN_MAX_TEMPS[2]: GLOBAL_MIN_MAX_TEMPS[2] = gpu_temp
        if gpu_temp > GLOBAL_MIN_MAX_TEMPS[3]: GLOBAL_MIN_MAX_TEMPS[3] = gpu_temp
        main_window.gpu_min_label.set_text(str(GLOBAL_MIN_MAX_TEMPS[2]))
        main_window.gpu_max_label.set_text(str(GLOBAL_MIN_MAX_TEMPS[3]))

        main_window.cpu_rpm_label.set_text(str(cpu_rpm))
        main_window.gpu_rpm_label.set_text(str(gpu_rpm))

    return True # Importante: deve ritornare True per far sì che GLib.timeout_add continui a chiamare la funzione.

def on_profile_changed(combo_box: Gtk.ComboBoxText):
    """
    Funzione callback richiamata quando l'utente seleziona un nuovo profilo dal ComboBox delle ventole.
    """
    selected_text = combo_box.get_active_text()
    profile_names = ["Auto", "Basic", "Advanced", "Cooler Booster"]
    try:
        profile_id = profile_names.index(selected_text) + 1
        apply_fan_profile(profile_id)
    except ValueError:
        print(f"ERRORE: Profilo '{selected_text}' non riconosciuto.")

def on_bct_changed(combo_box: Gtk.ComboBoxText):
    """
    Funzione callback richiamata quando l'utente seleziona una nuova soglia di carica batteria.
    """
    try:
        threshold = int(combo_box.get_active_text())
        # Scrive il valore nell'EC, aggiungendo un offset di 128 come da OFC.py originale
        write_ec(old_config.EC_BATTERY_THRESHOLD_ADDR, threshold + 128)
        update_config_file_battery_threshold(threshold)
    except ValueError:
        print("ERRORE: Valore soglia batteria non valido.")
    except Exception as e:
        print(f"ERRORE: Impossibile impostare soglia batteria: {e}")

# --- Costruzione dell'Interfaccia Utente ---

class FanControlWindow(Gtk.Window):
    """
    Classe principale della finestra dell'applicazione GTK per il controllo delle ventole.
    """
    def __init__(self):
        super().__init__(title="MSI Fan Control (Ultra 5 125H)") # Titolo aggiornato.
        self.set_default_size(450, 280) # Aumentato leggermente le dimensioni per più spazio.
        self.set_resizable(False) # Rendi la finestra non ridimensionabile per mantenere il layout.

        main_grid = Gtk.Grid()
        self.add(main_grid)
        main_grid.set_column_spacing(10)
        main_grid.set_row_spacing(10)
        main_grid.set_margin_start(20) # Margini più generosi
        main_grid.set_margin_end(20)
        main_grid.set_margin_top(20)
        main_grid.set_margin_bottom(20)
        main_grid.set_column_homogeneous(False) # Le colonne non avranno la stessa larghezza
        main_grid.set_row_homogeneous(False)    # Le righe non avranno la stessa altezza

        # Selettore del profilo ventole
        profile_label = Gtk.Label(label="Seleziona Profilo Ventola:")
        profile_label.set_halign(Gtk.Align.START) # Allinea a sinistra
        main_grid.attach(profile_label, 0, 0, 1, 1) # col, row, width, height

        self.profile_combo = Gtk.ComboBoxText()
        for p in ("Auto", "Basic", "Advanced", "Cooler Booster"):
            self.profile_combo.append_text(p)
        self.profile_combo.set_active(old_config.DEFAULT_FAN_PROFILE - 1)
        self.profile_combo.connect("changed", on_profile_changed)
        main_grid.attach(self.profile_combo, 1, 0, 2, 1) # Occupa 2 colonne per maggiore spazio

        # Separatore visivo
        main_grid.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), 0, 1, 5, 1)

        # Sezione Monitoraggio Temperature e RPM
        monitor_label = Gtk.Label(label="Monitoraggio (Temperatura °C / RPM)")
        monitor_label.set_halign(Gtk.Align.CENTER)
        main_grid.attach(monitor_label, 0, 2, 5, 1)

        # Header per le colonne di monitoraggio
        main_grid.attach(Gtk.Label(label=""), 0, 3, 1, 1) # Empty for row label
        main_grid.attach(Gtk.Label(label="Corrente"), 1, 3, 1, 1)
        main_grid.attach(Gtk.Label(label="Min"), 2, 3, 1, 1)
        main_grid.attach(Gtk.Label(label="Max"), 3, 3, 1, 1)
        main_grid.attach(Gtk.Label(label="RPM"), 4, 3, 1, 1)

        # Etichette CPU
        main_grid.attach(Gtk.Label(label="CPU"), 0, 4, 1, 1)
        self.cpu_curr_label = Gtk.Label(label="N/A"); main_grid.attach(self.cpu_curr_label, 1, 4, 1, 1)
        self.cpu_min_label = Gtk.Label(label="N/A"); main_grid.attach(self.cpu_min_label, 2, 4, 1, 1)
        self.cpu_max_label = Gtk.Label(label="N/A"); main_grid.attach(self.cpu_max_label, 3, 4, 1, 1)
        self.cpu_rpm_label = Gtk.Label(label="N/A"); main_grid.attach(self.cpu_rpm_label, 4, 4, 1, 1)

        # Etichette GPU
        main_grid.attach(Gtk.Label(label="GPU"), 0, 5, 1, 1)
        self.gpu_curr_label = Gtk.Label(label="N/A"); main_grid.attach(self.gpu_curr_label, 1, 5, 1, 1)
        self.gpu_min_label = Gtk.Label(label="N/A"); main_grid.attach(self.gpu_min_label, 2, 5, 1, 1)
        self.gpu_max_label = Gtk.Label(label="N/A"); main_grid.attach(self.gpu_max_label, 3, 5, 1, 1)
        self.gpu_rpm_label = Gtk.Label(label="N/A"); main_grid.attach(self.gpu_rpm_label, 4, 5, 1, 1)

        # Separatore visivo
        main_grid.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), 0, 6, 5, 1)

        # Selettore soglia di carica batteria
        battery_label = Gtk.Label(label="Soglia Carica Batteria (%):")
        battery_label.set_halign(Gtk.Align.START) # Allinea a sinistra
        main_grid.attach(battery_label, 0, 7, 1, 1)

        self.bct_combo = Gtk.ComboBoxText()
        for val in range(50, 101, 5):
            self.bct_combo.append_text(str(val))
        # Trova e imposta la selezione predefinita
        try:
            current_bct_index = list(range(50, 101, 5)).index(old_config.BATTERY_CHARGE_THRESHOLD)
            self.bct_combo.set_active(current_bct_index)
        except ValueError:
            self.bct_combo.set_active(0) # Se il valore non è nel range, seleziona 50%
        self.bct_combo.connect("changed", on_bct_changed)
        main_grid.attach(self.bct_combo, 1, 7, 2, 1) # Occupa 2 colonne

        # Avvia il timer per l'aggiornamento dei valori
        GLib.timeout_add(500, update_gui_values)

# Punto di ingresso dell'applicazione
if __name__ == "__main__":
    # La gestione iniziale del config.py non è più necessaria qui,
    # si assume che config.py esista e sia pre-configurato dall'utente.
    # Se il config.py non esiste, python solleverà un ImportError.
    # Puoi riaggiungere la logica di creazione guidata se lo desideri,
    # ma è più pulito avere il config.py gestito manualmente o da uno script di setup separato.

    # Rinomina la variabile globale per la finestra principale per chiarezza
    main_window = FanControlWindow()
    main_window.connect("destroy", Gtk.main_quit) # Collega la chiusura della finestra alla chiusura dell'applicazione GTK.
    main_window.show_all() # Mostra tutti gli elementi della finestra.
    Gtk.main() # Avvia il loop principale di GTK.