# qosic-sdk

An unofficial python sdk for the [QosIC](https://www.qosic.com/)
platform. This platform provides an api to enable mobile money payments
for businesses in Africa.

[![image](https://img.shields.io/pypi/v/qosic-sdk.svg)](https://pypi.python.org/pypi/qosic-sdk)
[![image](https://img.shields.io/pypi/pyversions/qosic-sdk)](https://github.com/Tobi-De/qosic-sdk)
[![Documentation Status](https://readthedocs.org/projects/qosic-sdk/badge/?version=latest)](https://qosic-sdk.readthedocs.io/en/latest/?version=latest)
[![image](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/Tobi-De/qosic-sdk/blob/main/LICENSE)
[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

------------------------------------------------------------------------

-   Free software: MIT license
-   Documentation: <https://qosic-sdk.readthedocs.io>.

## Features

-   Simple synchronous client to make your payment requests
-   Cover 100% of Qosic public api
-   Clean and meaningful exceptions
-   100 % test coverage
-   Configurable timeouts

## Quickstart

For those of you in a hurry, here's a sample code to get you started.

``` shell
pip install qosic-sdk
```

``` python
from dotenv import dotenv_values
from qosic import Client, bj

config = dotenv_values(".env")

moov_client_id = config.get("MOOV_CLIENT_ID")
mtn_client_id = config.get("MTN_CLIENT_ID")

login = config.get("SERVER_LOGIN")
password = config.get("SERVER_PASSWORD")

def main():
    phone = "229XXXXXXXX"
    mobile_carriers = [bj.MTN(id=mtn_client_id), bj.MOOV(id=moov_client_id)]
    client = Client(login=login, password=password, mobile_carriers=mobile_carriers)

    result = client.pay(phone=phone, amount=500)
    print(result)
    if result.success:
        print(f"Everything went fine")

    result = client.refund(reference=result.reference, phone=phone)
    print(result)


if __name__ == "__main__":
    main()
```

## Credits

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
project template.
