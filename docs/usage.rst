=====
Usage
=====


1. Initialize a client
----------------------

.. code-block:: python

    import os
    from qosic import Client, MTN, MOOV

    mtn_client_id = os.getenv("MTN_CLIENT_ID")
    moov_client_id = os.getenv("MTN_CLIENT_ID")
    server_login = os.getenv("SERVER_LOGIN")
    server_pass = os.getenv("SERVER_PASS")


    providers = [MTN(id=mtn_client_id), MOOV(id=moov_client_id)]

    client = Client(providers=providers,  login=server_login, password=server_pass)


The **Client** class is the main class of this library. the methods to perform the requests are defined on this class.
These are the available keyword arguments:

**providers** : List[Provider]

A list of your providers, even if you want to supply only one provider, this must be a list.


**login**: str

Your api authentication user.

**password**: str

Your api authentication password.

**debug**: bool = False

If set to true, the client will print to console each request and response.


2. Making a payment
-------------------

.. code-block:: python

    result = client.pay(phone=phone, amount=1000, first_name="User", last_name="TEST")


These are the available keyword arguments:

**phone**: str

This is an 11 numbers string made of country code and national number. For example you can do this:

.. code-block:: python

    client.pay(phone="22991617451", amount=1000, first_name="User", last_name="TEST")


**amount**: int

The payment amount, must be greater than zero.


**first_name**: str

The subscriber first name.


**last_name**: str

The subscriber last name.


3. Refunding a payment
----------------------

Refund are only available for MTN phone numbers for now. If you try a refund with a MOOV phone number, an
*AssertionError* will be raised.

.. code-block:: python

    from qosic import OPERATION_CONFIRMED

    result = client.refund(reference=result.reference)

    if result.success:
        print("successful refund")


These are the available keyword arguments:

**reference**: str

The transaction reference of your payment request. This value is available after every payment request
in the result object.

.. code-block :: python

    result = client.request_payment(
            phone=phone, amount=1000, first_name="User", last_name="TEST"
        )
    print(result.reference) # qhdfnqf7a63


4. Providers
------------

There are only two suppored providers for now, MTN and MOOV, and two
corresponding classes are available for them.

**MTN**

.. code-block:: python

    import os
    from qosic import MTN

    mtn_client_id = os.getenv("MTN_CLIENT_ID")

    MTN(id=mtn_client_id, step=30, timeout=60*2)


Payment request for this provider work in a way that involve polling to get the transaction status, you can check
on the Qosic_ docs for more details.
The MTN provider class can take the following keyword arguments:

**id** : str

Your client ID obviously.

**step** : int ( between 5 and 30) = 10 (the default)

Defines the amount of time to wait (in seconds) before each poll to get the transaction status. This value
must be inferior to the timeout value.

**timeout** : int ( between 60 and 180 ) = 120

The poll will be executed until the time elapsed is greater than the maximum timeout (in seconds).

**max_tries** : Optional[int]

Maximum number of times the fetch function will run. If set must validate this condition:

.. code-block:: console

    max_tries * step <= timeout


**reference_factory**: callable[[Payer], str]

A function to get a reference number, this function receive the payer information. The defualt function
return a 12 length string.

**MOOV**

.. code-block:: python

    import os
    from qosic import MOOV

    moov_client_id = os.getenv("MOOV_CLIENT_ID")

    MOOV(id=moov_client_id)


This provider does not provide extra configurations, so the setup process is very easy.

**id** : str

Your client ID.

**reference_factory**: callable[[Payer], str]

A function to get a reference number, this function receive the payer information. The defualt function
return a 12 length string.


5. Exceptions
-------------

Here is all the exceptions available :

- *ServerError* : raised when the qos server is busy or fails for some reason.
- *UserAccountNotFoundError* : raised when the phone number provided does not have a mobile money account.
- *ProviderNotFoundError* : raised when for the given phone number, the provider can't be identified.
- *InvalidPhoneNumberError* : raised when the phone number does not match the valid format.
- *InvalidClientIDError* : raised when the client ID does not match the provider or is incorrect.
- *InvalidCredentialsError* : raised when your api credentials are invalid.


.. _Qosic: https://www.qosic.com/docs/
.. _`open an issue`: https://github.com/Tobi-De/qosic-sdk/issues/new
