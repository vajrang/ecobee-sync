from cryptography.fernet import Fernet
from pyecobee import *

import config

ECOBEE_SYNC_TOKENS_FILENAME = 'tokens.txt'

ecobee_service = None
f = Fernet(config.ECOBEE_ENCRYPTION_KEY)


def enc(text):
    return f.encrypt(text.encode()).decode()


def dec(text):
    return f.decrypt(text.encode()).decode()


def _save_tokens_to_file(auth, access, refresh):
    try:
        with open(ECOBEE_SYNC_TOKENS_FILENAME, 'w') as tf:
            tf.write(enc(auth) + '\n')
            tf.write(enc(access) + '\n')
            tf.write(enc(refresh) + '\n')
    except Exception as ex:
        pass


def _read_tokens_from_file() -> tuple[str, str, str]:
    try:
        with open(ECOBEE_SYNC_TOKENS_FILENAME, 'r') as tf:
            lines = tf.read().split()
            auth, access, refresh = dec(lines[0]), dec(lines[1]), dec(lines[2])
            if all((auth, access, refresh)):
                return auth, access, refresh
    except Exception as ex:
        pass

    return None, None, None


def get_service():
    auth, access, refresh = _read_tokens_from_file()

    global ecobee_service
    ecobee_service = EcobeeService(
        thermostat_name=config.ECOBEE_THERMOSTAT_NAME,
        application_key=config.ECOBEE_APPLICATION_KEY,
        authorization_token=auth,
        access_token=access,
        refresh_token=refresh,
    )

    if not all((auth, access, refresh)):
        auth_response: EcobeeAuthorizeResponse = ecobee_service.authorize()

        pin = auth_response.ecobee_pin
        input(
            f"Please authorize this app by going to ecobee.com->My Apps->Add Application and entering '{pin}'\n"
            "Press <Enter> to continue... "
        )

        token_response: EcobeeTokensResponse = ecobee_service.request_tokens()

        auth = ecobee_service.authorization_token
        access = token_response.access_token
        refresh = token_response.refresh_token

        assert all((auth, access, refresh))
        _save_tokens_to_file(auth, access, refresh)

    token_response = ecobee_service.refresh_tokens()
    return ecobee_service
