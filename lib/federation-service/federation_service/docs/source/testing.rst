Testing the Federation Service
==============================


The Pytest library is used for automated testing of the Federation service and is divided into two test files.
The ``test_network.py`` set of tests are configuration related and check config validation regarding peers
and service json files. The bulk of the testing is done in ``test_uniform_federation.py``, which tests most
functions in both ``federation.py`` and ``operations.py``. Due to the nature of this service, being an aggregator
and communication tool between other services, many methods need to be mocked to simulate outgoing or incoming
messages from other services. 

If you are wanting to add more tests to the test suite, the ``test_structs.py`` found within ``tests/test_data``
contain a number of mocked classes to simulate responses along with data structures containing both input and 
output data.

The repo is hooked to Travis CI and will have all the tests run upon commit to any branch. If wanting to run the
tests locally, use the following command while in the main directory.

.. code-block:: bash

    $ pytest tests/

Optionally, you may add ``-vv`` to the end for more verbose output.