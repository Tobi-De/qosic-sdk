# qosic-sdk

---

[<img src="https://img.shields.io/pypi/v/qosic.svg">][pypi]
[<img src="https://img.shields.io/travis/Tobi-De/qosic.svg">][travis]
[<img src="https://readthedocs.org/projects/qosic/badge/?version=latest" alt="Documentation Status">][docs]

An unofficial python sdk for the [QosIC](https://www.qosic.com/) platform. This platform provides an api to enable mobile
money payments for businesses in Africa.

* Free software: MIT license
* Documentation: https://qosic.readthedocs.io.


## Supported Python versions

This library was tested with the following Python implementations, but it should work for all python 3.7 and above.

- Python 3.7
- Python 3.8

## Features

- Simple synchronous client to make your payment requests
- Clean and meaningful exceptions

##  TODOS

- Async Client for payment requests
- Configurable timeouts
- Enable Debug Logging
- 100 % test coverage

# Quickstart

For those of you in a hurry, here's a sample code to get you started.

```python
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
        result = client.request_payment(phone=phone, amount=2000)
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

```


## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.


[pypi]:https://pypi.python.org/pypi/qosic
[travis]:https://travis-ci.com/Tobi-De/qosic
[docs]:https://qosic.readthedocs.io/en/latest/?version=latest
