from qosic import Client, Provider, State
from qosic.exceptions import InvalidCredentialsError, RequestError
from dotenv import dotenv_values


config = dotenv_values(".env")

moov_client_id = config.get("MTN_CLIENT_ID")
mtn_client_id = config.get("MOOV_CLIENT_ID")
server_login = config.get("SERVER_LOGIN")
server_pass = config.get("SERVER_PASS")
# This is just for test purpose, you should directly pass the phone number
phone = config.get("PHONE_NUMBER")


def main():
    providers = [
        Provider(name="MTN", client_id=mtn_client_id),
        Provider(name="MOOV", client_id=moov_client_id),
    ]
    try:
        client = Client(providers=providers, login=server_login, password=server_pass)
        result = client.request_payment(
            phone=phone, amount=2000, first_name="tobi", last_name="DEGNON"
        )
    except (InvalidCredentialsError, RequestError) as e:
        print(e)
    else:
        if result.state == State.CONFIRMED:
            print(
                f"TransRef: {result.trans_ref} : Your requested payment to {result.phone}  for an amount "
                f"of {result.amount} has been successfully validated "
            )


if __name__ == "__main__":
    main()
