.. _development:

-----------------
Development Setup
-----------------

******************************
Standalone CNV Service  Setup
******************************

You will need Python 3.6.x to successfully run the service.

First, create and activate a  virtualenv with Python 3.6.x:

.. code-block:: bash
   
   python -m venv venv_name
   source venv_name/bin/activate

Once your virtual environment is created, you may clone `candig_cnv_service` by runing:

.. code-block:: bash

   git clone git@github.com:CanDIG/candig_cnv_service.git


Then you may go to the cloned directory and install it:

.. code-block:: bash

   pip install -e .


To start the service, you may run:

.. code-block:: bash
   
   candig_cnv_service


By default it will run on address 0.0.0.0 and port 8870. You may change it by running the previous command adding the desired address and port:

.. code-block:: bash
   
    candig_cnv_service --host 127.0.0.1 --port 8080
