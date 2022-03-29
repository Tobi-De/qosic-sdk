# qosic-sdk


[![pypi](https://img.shields.io/pypi/v/qosic-sdk.svg)](https://pypi.python.org/pypi/qosic-sdk)
[![travis](https://api.travis-ci.com/Tobi-De/qosic-sdk.svg)](https://travis-ci.com/Tobi-De/qosic-sdk)
[![python](https://img.shields.io/pypi/pyversions/qosic-sdk)](https://github.com/Tobi-De/qosic-sdk)
[![ReadTheDoc](https://readthedocs.org/projects/qosic-sdk/badge/?version=latest)](https://qosic-sdk.readthedocs.io/en/latest/?version=latest)
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/Tobi-De/dj-shop-cart/blob/master/LICENSE)
[![black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

An unofficial python sdk for the [QosIC](https://www.qosic.com/) platform. This platform provides an api to enable mobile
money payments for businesses in Africa.

* Free software: MIT license
* Documentation: https://qosic-sdk.readthedocs.io.

## Features

- Simple synchronous client to make your payment requests
- Cover 100% of Qosic public api
- Clean and meaningful exceptions
- 100 % test coverage
- Configurable timeouts

## Quickstart

For those of you in a hurry, here's a sample code to get you started.

```shell
    pip install qosic-sdk
```

```python

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
        client = Client(
            login=server_login,
            password=server_pass,
            providers=[MTN(id=mtn_client_id), MOOV(id=moov_client_id)],
        )
        result = client.pay(phone=phone, amount=500, first_name="User", last_name="TEST")
        print(result)
        if result.success:
            print(f"Everything went fine")

        result = client.refund(reference=result.reference)
        print(result)


    if __name__ == "__main__":
        main()

```

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
