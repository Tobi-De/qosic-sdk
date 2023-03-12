qosic-sdk
=========

An unofficial python sdk for the `QosIC <https://www.qosic.com/>`__
platform. This platform provides an api to enable mobile money payments
for businesses in Africa.


.. image:: https://img.shields.io/pypi/v/qosic-sdk.svg
        :target: https://pypi.python.org/pypi/qosic-sdk

.. image:: https://img.shields.io/pypi/pyversions/qosic-sdk
        :target: https://github.com/Tobi-De/qosic-sdk

.. image:: https://api.travis-ci.com/Tobi-De/qosic-sdk.svg
        :target: https://travis-ci.com/Tobi-De/qosic-sdk

.. image:: https://readthedocs.org/projects/qosic-sdk/badge/?version=latest
        :target: https://qosic-sdk.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
        :target: https://github.com/Tobi-De/qosic-sdk/blob/main/LICENSE

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
        :target: https://github.com/psf/black

----

-  Free software: MIT license
-  Documentation: https://qosic-sdk.readthedocs.io.

Features
--------

-  Simple synchronous client to make your payment requests
-  Cover 100% of Qosic public api
-  Clean and meaningful exceptions
-  100 % test coverage
-  Configurable timeouts

Quickstart
----------

For those of you in a hurry, here’s a sample code to get you started.

.. code:: shell

       pip install qosic-sdk

.. code:: python3


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

This package was created with
`Cookiecutter <https://github.com/audreyr/cookiecutter>`__ and the
`audreyr/cookiecutter-pypackage <https://github.com/audreyr/cookiecutter-pypackage>`__
project template.

