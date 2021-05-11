from qosic import Client, Provider
from dotenv import dotenv_values

config = dotenv_values(".env")

MTN_CLIENT_ID = config.get("MTN_CLIENT_ID")
MOOV_CLIENT_ID = config.get("MOOV_CLIENT_ID")
SERVER_LOGIN = config.get("SERVER_LOGIN")
SERVER_PASS = config.get("SERVER_PASS")
TEST_PHONE_NUMBER = config.get("TEST_PHONE_NUMBER")


def main():
    providers = [
        Provider(name="MTN", client_id=MTN_CLIENT_ID),
        Provider(name="MOOV", client_id=MOOV_CLIENT_ID),
    ]
    client = Client(providers=providers, login=SERVER_LOGIN, password=SERVER_PASS)
    result = client.request_payment(phone=TEST_PHONE_NUMBER, amount=2000)
    print(result)


if __name__ == "__main__":
    main()
