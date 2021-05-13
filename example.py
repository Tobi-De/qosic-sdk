from dotenv import dotenv_values

from qosic import Client, MtnConfig, MTN, MOOV, OPERATION_CONFIRMED
from qosic.exceptions import (
    InvalidCredentialsError,
    InvalidClientIdError,
    ServerError,
    RequestError,
)

config = dotenv_values(".env")

moov_client_id = config.get("MOOV_CLIENT_ID")
mtn_client_id = config.get("MTN_CLIENT_ID")
server_login = config.get("SERVER_LOGIN")
server_pass = config.get("SERVER_PASS")
# This is just for test purpose, you should directly pass the phone number
phone = config.get("PHONE_NUMBER")


def main():
    providers = [
        MTN(client_id=mtn_client_id, config=MtnConfig(step=30, timeout=60 * 2)),
        MOOV(client_id=moov_client_id),
    ]
    try:
        client = Client(
            providers=providers,
            login=server_login,
            password=server_pass,
            active_logging=True,
        )
        result = client.request_payment(
            phone=phone, amount=1000, first_name="User", last_name="TEST"
        )
    except (
        InvalidCredentialsError,
        InvalidClientIdError,
        ServerError,
        RequestError,
    ) as e:
        print(e)
    else:
        if result.state == OPERATION_CONFIRMED:
            print(
                f"TransRef: {result.trans_ref} -> Your requested payment to {result.phone}  for an amount "
                f"of {result.amount} has been successfully validated "
            )
        else:
            print(f"Payment rejected: {result}")
        # If you need to make a refund : (remember that refund are only available for MTN phone number right now)
        # result = client.request_refund(trans_ref=result.trans_ref, phone=phone)


if __name__ == "__main__":
    main()
