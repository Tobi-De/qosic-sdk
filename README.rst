=========
qosic-sdk
=========


.. image:: https://img.shields.io/pypi/v/qosic-sdk.svg
        :target: https://pypi.python.org/pypi/qosic-sdk

.. image:: https://api.travis-ci.com/Tobi-De/qosic-sdk.svg
        :target: https://travis-ci.com/Tobi-De/qosic-sdk

.. image:: https://readthedocs.org/projects/qosic-sdk/badge/?version=latest
        :target: https://qosic-sdk.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




An unofficial python sdk for the QosIC_ platform. This platform provides an api to enable mobile
money payments for businesses in Africa.


* Free software: MIT license
* Documentation: https://qosic-sdk.readthedocs.io.

Supported Python versions
-------------------------

This library was tested with the following Python implementations, but it should work for all python 3.6 and above.

- python 3.6
- Python 3.7
- Python 3.8


Features
--------

- Simple synchronous client to make your payment requests
- Clean and meaningful exceptions
- 100 % test coverage
- Configurable timeouts
- Enable Logging for debug purpose

TODOS
-----

- Async Client


Quickstart
----------

For those of you in a hurry, here's a sample code to get you started.

.. code-block:: shell

    pip install qosic-sdk

.. code-block:: python3

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
            print(client.collected_responses)
            # If you need to make a refund : (remember that refund are only available for MTN phone number right now)
            # result = client.request_refund(trans_ref=result.trans_ref, phone=phone)


    if __name__ == "__main__":
        main()


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _QosIC: https://www.qosic.com/
