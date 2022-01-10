from datetime import datetime

import pandas as pd
from influxdb import DataFrameClient, line_protocol
from influxdb.client import InfluxDBClient

from config import *

influx_reader = DataFrameClient(
    host="192.168.0.4",
    port=INFLUXDB_PORT,
    username=INFLUXDB_USER,
    password=INFLUXDB_PASS,
    database="rtlamr",
)

# set to test mode. when ready, change to actual destination
# and uncomment influx_writer.write line below
influx_writer = InfluxDBClient(
    host="192.168.0.4",
    port=INFLUXDB_PORT,
    username=INFLUXDB_USER,
    password=INFLUXDB_PASS,
    database="rtlamr_test",
)


def copy_meters_data(meters, format_type, start_time, end_time):
    """copy data for given meters from secondary to primary

    Args:
        meters (list[int]): list of meter ids
        format_type (str): lineformat type to use - must be 'SCM' or 'R900'
        start_time (datetime): start time of data window to copy
        end_time (datetime): end time of data window to copy
    """

    for m in meters:
        query_str = f"select * from rtlamr.autogen.rtlamr where time > '{start_time.isoformat()}' and time < '{end_time.isoformat()}' and endpoint_id='{m}'"
        res = influx_reader.query(query_str)

        df: pd.DataFrame = res['rtlamr']
        df = df[((df['protocol'] == 'SCM') | (df['protocol'] == 'R900')) & (df['msg_type'] == 'cumulative')]
        df = df.drop(['interval', 'outage'], axis=1, errors='ignore')

        for row in df.itertuples():
            nsts = line_protocol._convert_timestamp(row.Index)
            if format_type == 'SCM':
                str = f'rtlamr,endpoint_id={m},endpoint_type={row.endpoint_type},msg_type={row.msg_type},protocol={row.protocol} consumption={row.consumption}i {nsts}'
            elif format_type == 'R900':
                str = f'rtlamr,endpoint_id={m},endpoint_type={row.endpoint_type},msg_type={row.msg_type},protocol={row.protocol} backflow={row.backflow}i,consumption={row.consumption}i,leak={row.leak}i,leak_now={row.leak_now}i,nouse={row.nouse}i {nsts}'
            else:
                raise ValueError()

            print(str)
            # influx_writer.write(str, protocol='line', params={'db': influx_writer._database})


meters1 = [21212177, 11135205, 25775889, 14818315]
meters2 = [1549304240, 1549629534, 1563978630, 1564109680]

local_tz = datetime.now().astimezone().tzinfo
start_time = datetime(2022, 1, 7, 2, 43, tzinfo=local_tz)
end_time = datetime(2022, 1, 9, 11, 53, tzinfo=local_tz)

copy_meters_data(meters1, 'SCM', start_time, end_time)
copy_meters_data(meters2, 'R900', start_time, end_time)
