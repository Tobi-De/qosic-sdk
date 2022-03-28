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

Quickstart
----------

For those of you in a hurry, here's a sample code to get you started.

.. code-block:: shell

    pip install qosic-sdk

.. code-block:: python3

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


Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _QosIC: https://www.qosic.com/
