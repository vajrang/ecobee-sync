import json
import os

config_json = {}
try:
    with open('config.json', 'r') as conf:
        config_json: dict = json.load(conf)
except Exception as ex:
    pass

ECOBEE_THERMOSTAT_NAME = ''
ECOBEE_APPLICATION_KEY = os.getenv('ECOBEE_APPLICATION_KEY') or config_json.get('ECOBEE_APPLICATION_KEY')
ECOBEE_ENCRYPTION_KEY = os.getenv('ECOBEE_ENCRYPTION_KEY') or config_json.get('ECOBEE_ENCRYPTION_KEY')
