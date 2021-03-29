from influxdb import DataFrameClient

from config import *

influx = DataFrameClient(
    host=INFLUXDB_HOST,
    port=INFLUXDB_PORT,
    username=INFLUXDB_USER,
    password=INFLUXDB_PASS,
    database=INFLUXDB_DBSE,
)


def write_points_to_db(df):
    global influx
    influx.write_points(df, 'usage', tag_columns=['thermostat_id'])
