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

INFLUXDB_HOST = os.getenv('INFLUXDB_HOST') or config_json.get('INFLUXDB_HOST')
INFLUXDB_PORT = os.getenv('INFLUXDB_PORT') or config_json.get('INFLUXDB_PORT')
INFLUXDB_USER = os.getenv('INFLUXDB_USER') or config_json.get('INFLUXDB_USER')
INFLUXDB_PASS = os.getenv('INFLUXDB_PASS') or config_json.get('INFLUXDB_PASS')
INFLUXDB_DBSE = os.getenv('INFLUXDB_DBSE') or config_json.get('INFLUXDB_DBSE')
