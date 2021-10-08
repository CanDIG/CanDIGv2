.. _ingestion-workflow-example:

Ingestion workflow example
==========================

**1.** Create a project at :code:`/api/projects`:

.. code-block:: json

    {
      "title": "Test Project",
      "description": "About Test Project ..."
    }

201 Response example:

.. code-block:: json

    {
        "identifier": "998a36b2-7251-445d-81de-01a5affc5523",
        "datasets": [],
        "title": "Test Project",
        "description": "About Test Project ...",
        "created": "2020-10-15T20:17:03.029395Z",
        "updated": "2020-10-15T20:17:03.029395Z"
    }

**2.** Create a dataset at :code:`/api/datasets`:

Add project identifier from project response.

.. code-block:: json

    {
      "project": "998a36b2-7251-445d-81de-01a5affc5523",
      "title": "Test Dataset",
      "description": "About Test Dataset ...",
      "data_use": {
        "consent_code": {
          "primary_category": {
            "code": "GRU"
          },
          "secondary_categories": [
            {
              "code": "RU"
            }
          ]
        },
        "data_use_requirements": [
          {
            "code": "COL"
          }
        ]
      }
    }

201 Response example:

.. code-block:: json

    {
        "identifier": "86766cd6-f6bd-4d09-9d8a-308df4dd1fa1",
        "table_ownership": [],
        "title": "Test Dataset",
        "description": "About Test Dataset ...",
        "contact_info": "",
        "data_use": {
            "consent_code": {
                "primary_category": {
                    "code": "GRU"
                },
                "secondary_categories": [
                    {
                        "code": "RU"
                    }
                ]
            },
            "data_use_requirements": [
                {
                    "code": "COL"
                }
            ]
        },
        "linked_field_sets": [],
        "version": "version_2020-10-15 20:17:52.412173+00:00",
        "created": "2020-10-15T20:17:52.418029Z",
        "updated": "2020-10-15T20:17:52.418029Z",
        "project": "c488af39-d49b-4764-aa19-b86801220060"
    }

**3.** Create a table ownership at :code:`/api/table_ownership`:

Generate UUID for :code:`table_id` and add dataset identifier from dataset response.

.. code-block:: json

    {
        "table_id": "e08ff220-0f26-11eb-adc1-0242ac120002",
        "service_id": "metadata_service",
        "service_artifact": "metadata",
        "dataset": "86766cd6-f6bd-4d09-9d8a-308df4dd1fa1"
    }


201 Response example:

.. code-block:: json

    {
        "table_id": "e08ff220-0f26-11eb-adc1-0242ac120002",
        "service_id": "metadata_service",
        "service_artifact": "metadata",
        "dataset": "86766cd6-f6bd-4d09-9d8a-308df4dd1fa1"
    }


**4.** Create a table at :code:`/api/tables`:

Add table_id as :code:`ownership_record`.

.. code-block:: json

    {
        "ownership_record": "e08ff220-0f26-11eb-adc1-0242ac120002",
        "name": "metadata",
        "data_type": "phenopacket"
    }

**5.** Ingest phenopackets at :code:`/private/ingest`:

Add :code:`table_id`.

Specify path to the phenopackets data.

.. code-block:: json

    {
      "table_id": "e08ff220-0f26-11eb-adc1-0242ac120002",
      "workflow_id": "phenopackets_json",
      "workflow_params": {
        "phenopackets_json.json_document": "path/to/phenopackets.json"
      },
      "workflow_outputs": {
        "json_document": "path/to/phenopackets.json"
      }
    }