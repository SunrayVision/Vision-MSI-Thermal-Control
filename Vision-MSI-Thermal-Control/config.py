# config.py - Configurazioni specifiche per MSI Modern 15H AI C1MGT-096IT
# CPU: Intel Core Ultra 5 125H (considerata 10th Gen+ per gli indirizzi EC)

# --- Impostazioni Generali ---
# Profilo della ventola predefinito all'avvio:
# 1 = Auto, 2 = Basic, 3 = Advanced, 4 = Cooler Booster
DEFAULT_FAN_PROFILE = 2

# Soglia di carica massima della batteria (in percentuale, tra 50 e 100).
# Quando la batteria raggiunge questa percentuale, la ricarica si ferma.
BATTERY_CHARGE_THRESHOLD = 60

# Offset applicato alle velocità del profilo "Auto" per creare il profilo "Basic".
# Un valore positivo aumenta le velocità, un valore negativo le diminuisce.
# Range tipico: da -30 a +30. I valori saranno clippati tra 0 e 150.
BASIC_FAN_OFFSET = 0

# --- Indirizzi dell'Embedded Controller (EC) e Valori ---
# Questi valori sono specifici per le CPU Intel 10th Gen e successive,
# inclusa la tua Intel Core Ultra 5 125H (come indicato da OFC.py "LINE_YES").

# Indirizzo e valori per l'attivazione/disattivazione dei profili Auto/Advanced.
# [Indirizzo EC, Valore per Auto, Valore per Advanced]
EC_AUTO_ADV_CONTROL_ADDR = 0xd4
EC_AUTO_VALUE = 13  # Corrisponde al valore 0x0d
EC_ADVANCED_VALUE = 141 # Corrisponde al valore 0x8d

# Indirizzo e valori per il controllo di Cooler Booster.
# [Indirizzo EC, Valore per OFF, Valore per ON]
EC_COOLER_BOOSTER_CONTROL_ADDR = 0x98
EC_COOLER_BOOSTER_OFF_VALUE = 2
EC_COOLER_BOOSTER_ON_VALUE = 130

# Indirizzo EC per il controllo della soglia di carica della batteria.
#EC_BATTERY_THRESHOLD_ADDR = 0xe4 # Tipicamente con un offset di +128 sul valore %
EC_BATTERY_THRESHOLD_ADDR = 0xbf   # Nuovo - l'indirizzo corretto della batteria

# Indirizzi di memoria EC per leggere le temperature attuali di CPU e GPU.
# [Indirizzo CPU Temp, Indirizzo GPU Temp]
EC_TEMP_ADDRESSES = [0x68, 0x80]

# Indirizzi di memoria EC per leggere i giri al minuto (RPM) delle ventole CPU e GPU.
# [Indirizzo CPU RPM, Indirizzo GPU RPM]
EC_RPM_ADDRESSES = [0xc8, 0xca]

# Indirizzi di memoria EC dove scrivere le velocità dei 7 punti della curva delle ventole.
# [[Indirizzi CPU Fan Point 1-7], [Indirizzi GPU Fan Point 1-7]]
EC_FAN_CURVE_ADDRESSES = [
    [0x72, 0x73, 0x74, 0x75, 0x76, 0x77, 0x78], # CPU Fan Curve Addresses
    [0x8a, 0x8b, 0x8c, 0x8d, 0x8e, 0x8f, 0x90]  # GPU Fan Curve Addresses
]

# --- Curve di Velocità delle Ventole (Valori da 0 a 150) ---
# Ogni lista rappresenta 7 punti (presumibilmente per 7 soglie di temperatura).
# Questi valori sono mappati dal firmware EC a percentuali di velocità.

# Curva di velocità per il profilo "Auto".
# [[CPU Speeds], [GPU Speeds]]
AUTO_FAN_CURVE = [
    [0, 40, 48, 56, 64, 72, 80],  # Esempio: 0% fino alla prima soglia, 40% alla seconda, ecc.
    [0, 48, 56, 64, 72, 79, 86]
]

# Curva di velocità per il profilo "Advanced".
# Per un raffreddamento più aggressivo, si possono aumentare questi valori.
ADVANCED_FAN_CURVE = [
    # Esempio di curva più aggressiva per CPU (da testare)
    [0, 60, 70, 80, 90, 100, 120], # Aumentati i valori rispetto all'originale per essere più aggressivi
    # Esempio di curva più aggressiva per GPU (da testare)
    [0, 65, 75, 85, 95, 105, 125]  # Aumentati i valori rispetto all'originale per essere più aggressivi
]

# Costante di calibrazione per convertire i valori letti dall'EC in RPM.
# Questo valore è specifico del firmware MSI e dovrebbe essere 478000.
FAN_RPM_CALIBRATION_CONSTANT = 478000