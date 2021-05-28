from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from pyecobee import *

from influx_writer import *
from service import get_service

ecobee_service = get_service()

thermostat_summary_response: EcobeeThermostatsSummaryResponse = ecobee_service.request_thermostats_summary(
    selection=Selection(selection_type=SelectionType.REGISTERED.value, selection_match='')
)

# [('310130190774', 'Downstairs'), ('319264492718', 'Upstairs')]
thermostats = {x[0]: x[1] for x in [x.split(':') for x in thermostat_summary_response.revision_list]}
thermostat_ids = ','.join([t for t in thermostats])


def fetch_data_and_store(start: datetime, end: datetime):
    now = datetime.now(tz=timezone.utc)
    if end > now:
        end = now
    print(f'Fetching {start} to {end}')
    runtime_report_response = ecobee_service.request_runtime_reports(
        selection=Selection(selection_type=SelectionType.THERMOSTATS.value, selection_match=thermostat_ids),
        start_date_time=start,
        end_date_time=end,
        columns='auxHeat1,auxHeat2,auxHeat3,compCool1,compCool2,compHeat1,compHeat2,dehumidifier,dmOffset,'
        'economizer,fan,humidifier,hvacMode,outdoorHumidity,outdoorTemp,sky,ventilator,wind,zoneAveTemp,'
        'zoneCalendarEvent,zoneClimate,zoneCoolTemp,zoneHeatTemp,zoneHumidity,zoneHumidityHigh,'
        'zoneHumidityLow,zoneHvacMode,zoneOccupancy',
    )
    assert runtime_report_response.status.code == 0, \
        'Failure while executing request_runtime_reports:\n{0}'.format(runtime_report_response.pretty_format())

    timezonestr = 'US/Eastern'
    for rr in runtime_report_response.report_list:
        thermostat_id = rr.thermostat_identifier
        thermostat_name = thermostats[thermostat_id]
        df: pd.DataFrame = pd.Series(rr.row_list).str.split(',', expand=True)
        df = df.replace('', np.nan).astype(float, errors='ignore')

        df.columns = ['Date', 'Time', *(runtime_report_response.columns.split(','))]
        df['timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
        df['timestamp'] = df['timestamp'].dt.tz_localize(timezonestr, ambiguous='infer')
        df.set_index('timestamp', inplace=True)
        df.drop(['Date', 'Time'], axis=1, inplace=True)
        df['thermostat_id'] = thermostat_id

        write_points_to_db(df)


first = get_first_timestamp()
last = get_last_timestamp()
print(f'Last timestamp in db: {last}')
start = begin = last
# start = begin = datetime(2020, 1, 1, tzinfo=timezone.utc)
while True:
    if start > datetime.now(tz=timezone.utc):
        break
    end = start + timedelta(days=30)
    fetch_data_and_store(start, end)
    start = end

print()
