import sys
import json
import requests

"""
An ingest script that automates the initial data ingest for katsu service.

Make sure you have a config file named ingest.conf.json in the same dir as this script.

A sample ingest.conf.json is given below.

{
    "project_title": "project_1",
    "dataset_title": "dataset_1",
    "table_name": "table_1",
    "katsu_server_url": "http://example.com:4000",
    "phenopackets_json_location": "/home/user/v2/CanCOGen_synthetic_data/cancogen_phenopackets.json"
}

Usage (under active katsu virtualenv):
python ingest.py
"""


def load_config():
    """
    Load and return the config from ingest.conf.json
    """

    try:
        with open("ingest.conf.json") as f:
            return json.load(f)
    except FileNotFoundError:
        print(
            "The config file ingest.conf.json is missing. You must have it in the same dir as this script."
        )
        sys.exit()


def create_project(katsu_server_url, project_title):
    """
    Create a new Katsu project.

    Return the uuid of the newly-created project.
    """

    project_request = {
        "title": project_title,
        "description": "A new project."
    }

    try:
        r = requests.post(katsu_server_url + "/api/projects", json=project_request)
    except requests.exceptions.ConnectionError:
        print(
            "Connection to the API server {} cannot be established.".format(
                katsu_server_url
            )
        )
        sys.exit()

    if r.status_code == 201:
        project_uuid = r.json()["identifier"]
        print(
            "Project {} with uuid {} has been created!".format(
                project_title, project_uuid
            )
        )
        return project_uuid
    elif r.status_code == 400:
        print(
            "A project of title '{}' exists, please choose a different title, or delete this project.".format(
                project_title
            )
        )
        sys.exit()
    else:
        print(r.json())
        sys.exit()


def create_dataset(katsu_server_url, project_uuid, dataset_title):
    """
    Create a new dataset.

    Return the uuid of newly-created dataset.
    """
    dataset_request = {
        "project": project_uuid,
        "title": dataset_title,
        "data_use": {
            "consent_code": {
                "primary_category": {"code": "GRU"},
                "secondary_categories": [{"code": "GSO"}],
            },
            "data_use_requirements": [{"code": "COL"}, {"code": "PUB"}],
        },
    }

    r2 = requests.post(katsu_server_url + "/api/datasets", json=dataset_request)

    if r2.status_code == 201:
        dataset_uuid = r2.json()["identifier"]
        print(
            "Dataset {} with uuid {} has been created!".format(
                dataset_title, dataset_uuid
            )
        )
        return dataset_uuid
    elif r2.status_code == 400:
        print(
            "A dataset of title '{}' exists, please choose a different title, or delete this dataset.".format(
                dataset_title
            )
        )
        sys.exit()
    else:
        print(r2.json())
        sys.exit()


def create_table(katsu_server_url, dataset_uuid, table_name):
    """
    Create a new katsu table.

    Return the uuid of the newly-created table.
    """

    table_request = {
        "name": table_name,
        "data_type": "phenopacket",
        "dataset": dataset_uuid
    }

    r3 = requests.post(katsu_server_url + "/tables", json=table_request)

    if r3.status_code == 200 or r3.status_code == 201:
        table_id = r3.json()["id"]
        print("Table {} with uuid {} has been created!".format(table_name, table_id))
        return table_id
    else:
        print("Something went wrong...")
        sys.exit()


def ingest_phenopackets(katsu_server_url, table_id, phenopackets_json_location):
    """
    Ingest the phenopackets json
    """

    private_ingest_request = {
        "table_id": table_id,
        "workflow_id": "phenopackets_json",
        "workflow_params": {"phenopackets_json.json_document": phenopackets_json_location},
        "workflow_outputs": {"json_document": phenopackets_json_location},
    }

    print("Ingesting phenopackets, this may take a while...")

    r4 = requests.post(
        katsu_server_url + "/private/ingest", json=private_ingest_request
    )

    if r4.status_code == 200 or r4.status_code == 201 or r4.status_code == 204:
        print(
            "Phenopackets have been ingested from source at {}".format(
                phenopackets_json_location
            )
        )
    elif r4.status_code == 400:
        print(r4.text)
        sys.exit()
    else:
        print(
            "Something else went wrong when ingesting phenopackets, possibly due to duplications."
        )
        print(
            "Double check phenopackets_json_location config, or remove duplicated individuals from the database and try again."
        )
        sys.exit()


def main():
    config = load_config()

    print("Initializing...")
    print(
        "Warning: this script is only designed to handle the initial data ingestion of katsu service."
    )

    try:
        project_title = config["project_title"]
        dataset_title = config["dataset_title"]
        table_name = config["table_name"]
        katsu_server_url = config["katsu_server_url"]
        phenopackets_json_location = config["phenopackets_json_location"]
    except KeyError as e:
        print("Config file corrupted: missing key {}".format(str(e)))
        sys.exit()

    project_uuid = create_project(katsu_server_url, project_title)
    dataset_uuid = create_dataset(katsu_server_url, project_uuid, dataset_title)
    table_uuid = create_table(katsu_server_url, dataset_uuid, table_name)
    ingest_phenopackets(katsu_server_url, table_uuid, phenopackets_json_location)


if __name__ == "__main__":
    main()
