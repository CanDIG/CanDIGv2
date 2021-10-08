import os
import sys
import subprocess

"""
A script that automates the process of deleting the data
on the table passed as arguments.

Usage (under active katsu virtualenv):
python remove_from_db.py Project Individual Dataset
"""


def main():
    if len(sys.argv) <= 1:
        print("At least one table name should be passed as an argument")
        return

    script = (
        "from chord_metadata_service.chord.models import *;"
        "from chord_metadata_service.experiments.models import *;"
        "from chord_metadata_service.mcode.models import *;"
        "from chord_metadata_service.patients.models import *;"
        "from chord_metadata_service.phenopackets.models import *;"
        "from chord_metadata_service.resources.models import *;"
        "from chord_metadata_service.restapi.models import *;"
    )

    for table in sys.argv[1:]:
        response = subprocess.run(
            'python ../manage.py shell --command="{}"'.format(
                script + "{}.objects.all().delete();".format(table)
            ),
            shell=True,
            stderr=subprocess.PIPE,
        )
        if response.returncode:
            print('"{}" does not seem to be a valid table'.format(table))
        else:
            print("Deleted data on table {}".format(table))


if __name__ == "__main__":
    main()
