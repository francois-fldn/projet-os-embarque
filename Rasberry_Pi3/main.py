# lib standard python
import time
import logging
import argparse
from datetime import datetime
import json

# lib supplementaires
import smbus
import sqlite3
import paho.mqtt.client as mqtt

UID_LENGTH  = 16 # Nombre d'octets à lire
I2C_BUS     = 1 # Le bus I2C 

logger = logging.getLogger("Maitre I2C")
logging.basicConfig(
    level=logging.INFO,
    format="[%(name)s] [%(levelname)s] %(message)s"
)

parser = argparse.ArgumentParser(
  prog='Passerelle IoT',
  description="""
              """
)

parser.add_argument('room_id', 
                    type = int, 
                    help = 'L\'identifiant de la salle que l\'on veut contrôler',
                    default = 0x42
)

parser.add_argument('ip_mqtt', 
                    type = str, 
                    help = 'L\'adresse IP du broker MQTT',
                    default = "localhost"
)

# =====================================
# ==    FONCTIONS I2C                ==
# =====================================

def send_command(command: str):
    try:
        bus.write_byte(SLAVE_ADDRESS, ord(command))
        logger.info(f"Envoi de la commande de l'actionneur")
    except:
        logger.error(f"Erreur lors de l'envoi de la commande de l'actionneur : {e}")

def send_actuator_command_ok():
    send_command('O')

def send_actuator_command_not_ok():
    send_command('N')

def get_card_uid():
    try:
        data = bus.read_i2c_block_data(SLAVE_ADDRESS, 0x00, UID_LENGTH)
        uid_str = "".join([chr(x) for x in data if x != 0])
        return uid_str
    except Exception as e:
        logger.error(f"Erreur lors de la reception de l'uid de la carte : {e}")

# =====================================
# ==    FONCTIONS I2C                ==
# =====================================

# =====================================
# ==    FONCTIONS DE FETCH BDD       ==
# =====================================

def get_room_permissions():
    global connection
    c = connection.cursor()
    query = "SELECT min_level, min_level_spe FROM room WHERE room_id = ?"
    c.execute(query, (SLAVE_ADDRESS,))
    resultat = c.fetchone() 
    if resultat:
        return (resultat[0], resultat[1])
    else:
        return None

def get_user_permission(uid):
    global connection
    c = connection.cursor()
    query = "SELECT level, level_spe FROM employees WHERE uid = ?"
    c.execute(query, (uid,))
    resultat = c.fetchone()
    return (resultat[0], resultat[1]) if resultat else None

# =====================================
# ==    FONCTIONS DE FETCH BDD       ==
# =====================================

def is_permitted(perm_room, perm_user):
    (level_room, spe_room) = perm_room
    (level_user, spe_user) = perm_user
    return level_room <= level_user or spe_room <= spe_user

def send_mqtt(uid: str, decision: str):
    try:
        data = dict()
        data["timestamp"] = datetime.now().timestamp()
        data["uid"] = uid
        data["decision"] = decision

        data_final = json.dumps(data)
        topic = f"room_{SLAVE_ADDRESS}/transactions_carte"
        client.publish(topic, data_final)
        logger.info(f"Transaction envoyée sur le topic room_{SLAVE_ADDRESS}/transactions_carte")
    except Exception as e:
        logger.error(f"{e}")


def main():
    logger.info(f"Récuperation des permissions de la salle {SLAVE_ADDRESS}")
    
    room_permissions = get_room_permissions()

    if room_permissions : logger.info(f"Permissions de la salle {SLAVE_ADDRESS} obtenues : {room_permissions}")
    else:
        logger.error(f"La salle {SLAVE_ADDRESS} n'existe pas.")
        exit(1)

    logger.info(f"En attente de carte...")

    while True:
        uid = get_card_uid()
        if uid:
            logger.info(f"Récuperation des permissions de l'employé : {uid}")
            employee_permissions = get_user_permission(uid)
            state = "NON_EXISTANT"

            if employee_permissions: 
                logger.info(f'Employé no. {uid}, vérification des permissions d\'accès')
                res = is_permitted(room_permissions, employee_permissions)

                if res:
                    state = "ALLOWED"
                    logger.info(f"Niveau de sécurité vérifié, accès autorisé")
                    send_actuator_command_ok()

                else:
                    state = "NON_ALLOWED"
                    logger.warning(f"Niveau de sécurité trop bas, accès refusé")
                    send_actuator_command_not_ok()

            else:
                logger.error(f"Employé no. {uid}, n'existe pas dans la base de données")
                send_actuator_command_not_ok()
            
            send_mqtt(uid, state)
            
        time.sleep(0.5)

if __name__ == "__main__":

    args = parser.parse_args()
    SLAVE_ADDRESS = args.room_id
    MQTT_BROKER_HOST = args.ip_mqtt

    not_connected = True
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    while not_connected:
        try:
            client.connect(MQTT_BROKER_HOST, 1883, 60)
            logger.info(f"Connection au broker MQTT réussie")
            not_connected = False
        except Exception as e:
            logger.error(f"Erreur de connexion au broker MQTT : {e}")

    not_connected = True
    while not_connected:
        try:
            connection = sqlite3.connect('rooms-control.db')
            logger.info(f'Connection a la bdd réussie')
            not_connected = False
        except Exception as e:
            logger.error(f"Problème de connection a la bdd : {e}")

    not_connected = True
    while not_connected:
        try:
            bus = smbus.SMBus(I2C_BUS)
            logger.info(f'Connection au bus I2C réussie')
            not_connected = False
        except Exception as e:
            logger.error(f"Impossible d'ouvrir le bus I2C : {e}")


    main()
