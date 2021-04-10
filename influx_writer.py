from datetime import datetime

import pandas as pd
from influxdb import DataFrameClient

from config import *

influx = DataFrameClient(
    host=INFLUXDB_HOST,
    port=INFLUXDB_PORT,
    username=INFLUXDB_USER,
    password=INFLUXDB_PASS,
    database=INFLUXDB_DBSE,
)


def write_points_to_db(df: pd.DataFrame):
    global influx
    # workaround to handle that DataFrameClient doesn't handle NaN values
    # https://github.com/influxdata/influxdb-python/issues/422
    # Ideally this should be the call
    # influx.write_points(df, 'usage', tag_columns=['thermostat_id'])
    columns = list(df.columns)
    columns.remove('thermostat_id')
    for c in columns:
        influx.write_points(df[[c, 'thermostat_id']].dropna(), 'usage', tag_columns=['thermostat_id'])


def get_first_timestamp() -> datetime:
    global influx
    res = influx.query("""
            SELECT * FROM ecobee.autogen.usage ORDER BY asc LIMIT 1
        """)
    if not res:
        return None
    retval = res['usage'].index[0]
    return retval.to_pydatetime()


def get_last_timestamp() -> datetime:
    global influx
    res = influx.query("""
            SELECT * FROM ecobee.autogen.usage ORDER BY desc LIMIT 1
        """)
    if not res:
        return None
    retval = res['usage'].index[0]
    return retval.to_pydatetime()
