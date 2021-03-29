from pyecobee import *

from service import get_service

ecobee_service = get_service()

thermostat_summary_response = ecobee_service.request_thermostats_summary(
    selection=Selection(
        selection_type=SelectionType.REGISTERED.value, selection_match='', include_equipment_status=True
    )
)
print(thermostat_summary_response.pretty_format())

# Only set the include options you need to True. I've set most of them to True for illustrative purposes only.
selection = Selection(
    selection_type=SelectionType.REGISTERED.value,
    selection_match='',
    include_alerts=True,
    include_device=True,
    include_electricity=True,
    include_equipment_status=True,
    include_events=True,
    include_extended_runtime=True,
    include_house_details=True,
    include_location=True,
    include_management=True,
    include_notification_settings=True,
    include_oem_cfg=False,
    include_privacy=False,
    include_program=True,
    include_reminders=True,
    include_runtime=True,
    include_security_settings=False,
    include_sensors=True,
    include_settings=True,
    include_technician=True,
    include_utility=True,
    include_version=True,
    include_weather=True,
)
thermostat_response = ecobee_service.request_thermostats(selection)
print(thermostat_response.pretty_format())
assert thermostat_response.status.code == 0, 'Failure while executing request_thermostats:\n{0}'.format(
    thermostat_response.pretty_format()
)
