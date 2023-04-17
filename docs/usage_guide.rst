=====
Usage Guide
=====

Overview
--------

The ``Client`` class serves as the primary interface for communication with the QosIc API within the **qosic-sdk** package.
This guide offers comprehensive instructions on how to effectively utilize the ``Client`` class for interacting with the payment platform API.

Initialization
--------------

To use the ``Client`` class, you need to initialize an instance of it with the required parameters. The following parameters are available for initialization:

* **login**: Your server authentication login/user.
* **password**: Your server authentication password.
* **mobile_carriers**: The list of configured mobile carriers.
* **base_url**: The QosIC server root domain, if you ever need to change it. Default is `https://qosic.net:8443 <https://qosic.net:8443>`_.
* **logger**: Custom logger for logging API requests and responses.

.. code-block:: python

    from qosic import Client, bj

    mobile_carriers = [bj.MTN("mtn_client_id"), bj.MOOV("moov_client_id")]
    client = Client(login="your_login", password="your_password", mobile_carriers=mobile_carriers)


Making Payments
---------------

To make a payment using the ``Client`` class, you can call the ``pay()`` method with the following parameters:

* **phone**: The phone number of the payer.
* **amount**: The amount to be paid.
* **first_name** (optional): The first name of the payer. Default is an empty string.
* **last_name** (optional): The last name of the payer. Default is an empty string.

.. code-block:: python

    result = client.pay(phone="22901020304", amount=1000, first_name="John", last_name="Doe")
    if result.success:
        print("Payment successful")
    else:
        print("Payment failed. Error: ", result.response)

Processing Refunds
------------------

To request a refund using the ``Client`` class, you can call the ``refund()`` method with the following parameters:

* **reference**: The reference ID of the original payment, available in the ``Result`` object returned by the ``pay()`` method.
* **phone**: The phone number of the payer.

.. code-block:: python

    result = client.refund(reference="1234567890", phone="22901020304")
    if result.success:
        print("Refund successful")
    else:
        print("Refund failed. Error: ", result.response)


``Result`` class
------------------

A helper class that encapsulates the response from the server for a payment or refund request made using the Python SDK for the Payment Platform API.

-   **status** (Result.Status): The status of the request, which can be either ``Result.Status.CONFIRMED`` or ``Result.Status.FAILED``.
-   **reference** (str): The reference number associated with the request.
-   **phone** (str): The phone number associated with the request.
-   **mobile_carrier** (MobileCarrier): The mobile carrier associated with the request.
-   **response** (httpx.Response): The HTTP response object returned from the server.

**Properties**

-   **success** (bool): A property that indicates whether the request was successful or not. Returns ``True`` if the ``status``
    is ``Result.Status.CONFIRMED``, indicating a successful request, and ``False`` otherwise.

Logging
-------

The ``Client`` class uses the ``logging`` module to log API requests and responses. You can customize the logging behavior and format
by passing a custom logger to the ``Client`` class during initialization. For debugging purpose you can configure the logging
level to display all the interactions with the payment API.

.. code-block:: python
    import logging

    logging.basicConfig(level=logging.DEBUG)

    client = Client(login="your_login", password="your_password", mobile_carriers=mobile_carriers)
    client.pay(phone="22901020304", amount=1000) # will log everything in your terminal


Error Handling
--------------

If everything goes well, the ``pay()`` and ``refund()`` methods return a ``Result`` if the request completely fails to be
processed by the server, one the exceptions listed below is raised.

* **ServerError** : raised when the qos server is busy or fails for some reason.
* **UserAccountNotFoundError** : raised when the phone number provided does not have a mobile money account.
* **ProviderNotFoundError** : raised when for the given phone number, the provider can't be identified.
* **InvalidPhoneNumberError** : raised when the phone number does not match the valid format.
* **InvalidClientIDError** : raised when the client ID does not match the provider or is incorrect.
* **InvalidCredentialsError** : raised when your api credentials are invalid.

Best Practices
--------------

Use a task queue
================

To optimize the processing of payment requests, it's important to note that API response times may vary depending on the mobile carrier used.
Factors such as waiting for customer approval or polling for transaction results can cause delays.
To prevent your server from being blocked during this process, it's recommended to implement asynchronous processing using a task queue.

When using a task queue, you can periodically poll a specific endpoint on your server to check the status of the transaction.
Alternatively, you can utilize server-side events to push real-time transaction status updates to the frontend.
This allows you to efficiently display the transaction status to your users on the frontend, ensuring a smooth user experience.

Use environment variables for your credentials
==============================================

You should never hardcode your credentials in your code. Instead, you should use environment variables to store your credentials and then access them in your code.
This includes your **login**, **password**, and  the **client_id** of all the mobile carriers.




