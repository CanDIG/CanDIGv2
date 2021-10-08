Installation
============


After pulling the repo, create a virtual environment utilizing Python 3.7+ and install the requirements:

.. code-block:: bash

    $ pip install -r requirements.txt

After installation, the Federation service should first be configured.


Configuration
-------------
There are three sections which need to be configured to properly set up the Federation service.

1. The ``__main__.py`` file in ``federation_service/candig_federation``
2. The ``peers.json`` and ``services.json`` files in ``federation_service/configs``
3. The ``federation.ini`` configuration file for uWSGI


\__main__.py
^^^^^^^^^^^^

This file acts as the driver for the Federation service as well as contains a number of default configuration settings.

.. code-block:: python

    parser.add_argument('--port', default=8890)
    parser.add_argument('--host', default='ga4ghdev01.bcgsc.ca')
    parser.add_argument('--logfile', default="./log/federation.log")
    parser.add_argument('--loglevel', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'])
    parser.add_argument('--services', default="./configs/services.json")
    parser.add_argument('--peers', default="./configs/peers.json")
    parser.add_argument('--schemas', default="./configs/schemas.json")

Any of these keyword arguments may be altered when running the service through the command line. Additional arguments
may be added by copying the format above.

============== ============
Argument        Explanation
-------------- ------------
``--port``      specifies the port the service should listen on.
``--host``      specifies the host address for the service.
``--logfile``   specifies the file which messages are logged to.
``--loglevel``  controls the verbosity of the logs.
``--services``  specifies a configuration file that tells Federation which services it should know about.
``--peers``     specifies a configuration file that tells Federation which peers it should know about.
============== ============



JSON configs
^^^^^^^^^^^^

Two types of configuration files are located in the `configs` folder, with examples of each marked by ``_ex``. Valid instances
of both files are required in order to start the Federation service.

.. code-block:: json

  {
    "peers": {
        "p1": "http://peer1.com",
        "p2": "http://peer2.com"
    }
  }

Currently, each peer listed in a ``peers`` configuration file should correspond with the Tyk API Gateway for each CanDIG node,
including the one running in the node this Federation service is running in.


.. code-block:: json

 {
   "services": {
        "rnaget": "http://example1.com",
        "datasets": "http://example2.com"
   }
 }

Each service should correspond to a CanDIG service accessible by the Federation service. Due to the way request parsing works,
it's important to utilize the same service key name as its base API path.


uWSGI Configuration
^^^^^^^^^^^^^^^^^^^

The ``federation.ini`` file located in the top level of the directory controls uWSGI. The only portion that would need to be
altered is the ``chdir`` location and ``socket`` output location.

.. code-block:: ini

    [uwsgi]
    module = wsgi:application
    chdir = /home/dnaidoo/Documents/federation_service

    master = true
    processes = 3

    gid = candig
    socket = /home/dnaidoo/Documents/federation_service/federation.sock
    chmod-socket = 660
    vacuum = true

    die-on-term = true



