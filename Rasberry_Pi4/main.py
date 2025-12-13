import smbus
import time

# Adresse I2C de l'ATmega328P (0x42 en Hexadécimal)
SLAVE_ADDRESS = 0x42 

# Commande pour demander l'UID (0x03)
COMMAND_UID = 0x03 

# Nombre d'octets à lire (taille de votre tableau current_uid)
UID_LENGTH = 16

# Le bus I2C (généralement 1 sur les modèles récents de Raspberry Pi)
I2C_BUS = 1 

try:
    # Initialisation du bus
    bus = smbus.SMBus(I2C_BUS)
    
    print(f"Connexion à l'esclave I2C à l'adresse 0x{SLAVE_ADDRESS:02x}...")
    
    # Étape 1 : Envoyer la commande (WRITE)
    # L'esclave ATmega reçoit 0x03 et le stocke dans twi_command.
    bus.write_byte(SLAVE_ADDRESS, COMMAND_UID)
    time.sleep(0.01) # Petit délai pour laisser le temps à l'esclave de traiter la commande
    
    print(f"Commande 0x{COMMAND_UID:02x} envoyée. Tentative de lecture de {UID_LENGTH} octets...")

    # Étape 2 : Lire les données (READ)
    # Le Raspberry Pi demande à lire les données, ce qui déclenche l'envoi de l'UID par l'ISR TWI.
    uid_bytes = bus.read_i2c_block_data(SLAVE_ADDRESS, 0x00, UID_LENGTH)
    
    # Affichage des résultats
    uid_hex = ''.join([f'{b:02x}' for b in uid_bytes])
    
    print("-" * 25)
    print(f"UID Reçu (Hex) : {uid_hex.upper()}")
    
    # Si le premier octet est 0xFF, cela indique souvent une erreur ou une réponse par défaut
    if uid_bytes[0] == 0xFF:
         print("(Note: Le code 0xFF peut indiquer une erreur ou une absence de commande précédente.)")
    print("-" * 25)

except FileNotFoundError:
    print("ERREUR: Le périphérique I2C n'est pas trouvé. Avez-vous activé l'I2C dans raspi-config?")
except Exception as e:
    print(f"Une erreur I2C s'est produite : {e}")