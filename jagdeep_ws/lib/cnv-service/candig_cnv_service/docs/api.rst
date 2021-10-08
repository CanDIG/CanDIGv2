.. _api:

**************************
API Usage & Sample Queries
**************************

.. warning::

    This guide is a work in progress, and it is incomplete.

This section will provide instructions on API usages.

--------------
Fetch Patients
--------------
Description: To fetch all the patients, make a query to /cnvariant/patients endpoint passing no arguments at all.
The response is a list similar to this:

.. code-block:: json

 [
   "d290f1ee-6c54-4b01-90e6-d701748f0851"
 ]


-------------
Fetch Samples
-------------
Description: To fetch all the samples of a patient, make a query to /cnvariant/patients/samples endpoint passing the patient_id as an argument.
Example:

.. code-block:: bash
   
    /cnvariant/patients/samples?patient_id=d290f1ee-6c54-4b01-90e6-d701748f0851

In addition, you can fetch samples using tags:

.. code-block:: bash
    
    /cnvariant/patients/samples?patient_id=d290f1ee-6c54-4b01-90e6-d701748f0851&tags=canadian,ovarian

Or description

.. code-block:: bash
    
    /cnvariant/patients/samples?patient_id=d290f1ee-6c54-4b01-90e6-d701748f0851&description=Canadian

Or both:

.. code-block:: bash
    
    /cnvariant/patients/samples?patient_id=d290f1ee-6c54-4b01-90e6-d701748f0851&description=Canadian&tags=canadian,ovaria

The response is a json object similar to this:

.. code-block:: json

 {"patient_id": "d290f1ee-6c54-4b01-90e6-d701748f0851",
 "samples": [{"access_level": 2,
              "created": "2020-01-16 08:09:21.347777",
              "description": "Canadian Sample",
              "sample_id": "COV2202",
              "tags": ["Canada", "Ovarian"]}]}

--------------
Fetch Segments
--------------
Description: To fetch a segment, make a query to /cnvariant/patients/samples/cnv endpoint passign the  patient_id, sample_id, chromosome_number, start_position and end_position.
Example:

.. code-block:: bash

    /cnvariant/patients/samples/cnv?patient_id=d290f1ee-6c54-4b01-90e6-d701748f0851&sample_id=COV2202&chromosome_number=5&start_position=12522&end_position=34326

The response is a json object similar to this:

.. code-block:: json

 [{"chromosome_number": "5",
   "copy_number": -0.16,
   "copy_number_ploidy_corrected": 0,
   "end_position": 23425,
   "start_position": 12523},
  {"chromosome_number": "5",
   "copy_number": -0.16,
   "copy_number_ploidy_corrected": 0,
   "end_position": 34326,
   "start_position": 23426}]
