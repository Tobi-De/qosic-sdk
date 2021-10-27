=======
History
=======

2.0.0 (2021-10-27)
------------------

* Now using polling2 and the phonenumbers python packages


1.1.3 (2021-05-22)
------------------

* add support for context manager to the Client class


1.1.2 (2021-05-20)
------------------

* Add more prefixes to MTN and MOOV prefixes
* Update docs


1.1.1 (2021-05-20)
------------------

* Update MTN and MOOV prefixes


1.1.0 (2021-05-19)
------------------

* Change MtnConfig step default and minimal value.
* Add exception list to the docs.
* Remove PollRuntimeError, now the poll function fails while raising the right exception.
* When active_logging is set to True, the client now collect responses in the client property *collected_responses*.


1.0.2 (2021-05-16)
------------------

* Change timeout defaults.
*Update docs.


1.0.1 (2021-05-14)
------------------

* Write some tests.
* The internal http client handles non-json responses better.


1.0.0 (2021-05-13)
------------------

* First release on PyPI.

