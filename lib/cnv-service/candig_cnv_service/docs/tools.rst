Tools
=====

The tools module currently provides a CLI ingest script to add entire CNV files to the service.
This ingest is divided between an ``Ingester`` Class located in ``ingester.py``, which provides
database methods and file type checking and the ``cnv_ingest.py`` script which controls how the
file is ingested.

The Ingester class currently accepts CSV and TSV formatted CNV files. These files should contain
the following headers otherwise they will not be accepted:

================= ============== ============ =========== ============================
chromosome_number start_position end_position copy_number copy_number_ploidy_corrected
================= ============== ============ =========== ============================

Other than header validation, the ingester **does not** check the contents of the file
at this time. It is up to the uploader to insure that the data is valid.


Ingest Usage
============

The ``cnv_ingest`` script takes a number of parameters in addition to the CNV file itself.

================  ============
Argument          Explanation
----------------  ------------
``patient``       Patient UUID.
``sample``        Sample UUID.
``file``          Location of the CNV file.
``--database``    Location of the database (uses service default if not provided).
``--sequential``  Boolean. If set to True, uploads the CNV sequentially if PK errors 
                  are encountered during the bulk ingest. This will allow for a partial 
                  upload of the CNV along with details of which segments are causing errors.
================  ============

The first three arguments need to be provided in the order shown above, with the last two 
being optional.

Example:

.. code-block:: bash

    python candig_cnv_service/tools/cnv_ingest.py e9200a68-1233-40d3-983f-4370b7d17ca8 8bc4d487-6163-46b7-b406-d6a308fec95e  /home/dashaylan/Documents/GSC/cnv_service/cnv_1.csv --sequential True

