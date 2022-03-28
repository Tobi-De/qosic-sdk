from dotenv import dotenv_values

from qosic import Client, MTN, MOOV

config = dotenv_values(".env")

moov_client_id = config.get("MOOV_CLIENT_ID")
mtn_client_id = config.get("MTN_CLIENT_ID")
server_login = config.get("SERVER_LOGIN")
server_pass = config.get("SERVER_PASSWORD")
# This is just for test purpose, you should directly pass the phone number
phone = config.get("PHONE_NUMBER")


def main():
    providers = [MTN(id=mtn_client_id), MOOV(id=moov_client_id)]
    client = Client(
        providers=providers,
        login=server_login,
        password=server_pass,
        debug=True
    )
    result = client.pay(phone=phone, amount=500, first_name="User", last_name="TEST")
    print(result)
    if result.success:
        print(f"Everything went fine")

    result = client.refund(reference=result.reference)
    print(result)


if __name__ == "__main__":
    main()
