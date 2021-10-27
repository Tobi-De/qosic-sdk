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


    providers = [MTN(client_id=mtn_client_id),MOOV(client_id=moov_client_id)]

    client = Client(providers=providers,  login=server_login, password=server_pass)


The **Client** class is the main class of this library. the methods to perform the requests are defined on this class.
These are the available keyword arguments:

**providers** : List[Provider]

A list of your providers, even if you want to supply only one provider, this must be a list.


**login**: str

Your api authentication user.

**password**: str

Your api authentication password.

**active_logging**: bool = False

If set to true, the client will log each request and response.


2. Making a payment
-------------------

.. code-block:: python

    result = client.request_payment(
            phone=phone, amount=1000, first_name="User", last_name="TEST"
        )



These are the available keyword arguments:

**phone**: PhoneNumber

This use the PhoneNumber class from the phonenumbers package. For example you can do this:

.. code-block:: python

    import phonenumbers
    phone = phonenumbers.parse("+22991617451")


**amount**: int

The payment amount, must be greater than zero.


**first_name**: Optional[str]

The subscriber first name.


**last_name**: Optional[str]

The subscriber last name.





3. Refunding a payment
----------------------

Refund are only available for MTN phone numbers for now. If you try a refund with a MOOV phone number, an
*AssertionError* will be raised.

.. code-block:: python

    from qosic import OPERATION_CONFIRMED

    result = client.request_refund(trans_ref=result.trans_ref, phone=phone)

    if result.state == OPERATION_CONFIRMED:
        print("successful refund")

    #-------------------------------------

    if result.state:
        print("successful refund")


These are the available keyword arguments:

**trans_ref**: str

The transaction reference of your payment request. This value is availablea after every payment request
in the result object.

.. code-block :: python

    result = client.request_payment(
            phone=phone, amount=1000, first_name="User", last_name="TEST"
        )
    print(result.trans_ref) # qhdfnqf7a63


**phone**: str

The phone number used. Example : 229XXXXXXXX





4. Providers
------------

There are only two suppored providers for now, MTN and MOOV, and two
corresponding classes are available for them.

**MTN**

.. code-block:: python

    import os
    from qosic import MTN, MtnConfig

    mtn_client_id = os.getenv("MTN_CLIENT_ID")

    MTN(client_id=mtn_client_id, config=MtnConfig(step=30, timeout=60*2))


Payment request for this provider work in a way that involve polling to get the transaction status, you can check
on the Qosic_ docs for more details. The MtnConfig class is a helper class that helps you define the
step and timeout related to the poll function.
The MTN provider class can take the following keyword arguments:

**client_id** : str

Your client ID obviously.

**config** : Optional[MtnConfig]

An instance of the **MtnConfig** class that represents your poll configurations. This argument is optional.
These are the available keyword arguments:

- *step* : int ( between 30 and 90) = 60 (the default)

Defines the amount of time to wait (in seconds) before each poll to get the transaction status. This value
must be inferior to the timeout value.

- *timeout* : int ( between 60 and 300 ) = 120

The poll will be executed until the time elapsed is greater than the maximum timeout (in seconds).

- *max_tries* : Optional[int]

Maximum number of times the fetch function will run. This values validate this condition:

.. code-block:: console

    max_tries * step <= timeout


**allowed_prefixes**: List[str]

The list of the phone number valid prefixes for this provider. The default value should be good enough, you will probably
never need to change it.


**MOOV**

.. code-block:: python

    import os
    from qosic import MOOV

    moov_client_id = os.getenv("MMOOV_CLIENT_ID")

    MOOV(client_id=moov_client_id)


These provider does not provide extra configurations, so the setup process is very easy.


**client_id** : str

Your client ID.

**allowed_prefixes**: List[str]

The list of the phone number valid prefixes for this provider. The default value should be good enough, you will probably
never need to change it.


5. Exceptions
-------------

Here is all the exceptions available :

- *ServerError* : raised when the qos server is busy or fails for some reason.
- *UserAccountNotFound* : raised when the phone number provided does not have a mobile money account.
- *ProviderNotFoundError* : raised when for the given phone number, the provider can't be identified.
- *InvalidPhoneError* : raised when the phone number does not match the valid format.
- *InvalidClientIdError* : raised when the client ID does not match the provider or is incorrect.
- *InvalidCredentialsError* : raised when your api credentials are invalid.
- *RequestError*: raised when the internal http client failed to make a request, check your logs and if there is no obvious solution to your problem, `open an issue`_ on the repository.




.. _Qosic: https://www.qosic.com/docs/
.. _`open an issue`: https://github.com/Tobi-De/qosic-sdk/issues/new
