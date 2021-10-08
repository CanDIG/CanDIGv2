import json

from django.core.management.base import BaseCommand
from chord_metadata_service.chord.models import Project, Dataset


class Command(BaseCommand):
    help = """
        Creates a Katsu/Bento dataset in the database.
        Arguments: "title" "description" "contact_info" "project" ./path/to/data_use.json
    """

    def add_arguments(self, parser):
        parser.add_argument("title", action="store", type=str, help="The title for the new dataset")
        parser.add_argument("description", action="store", type=str, help="The description for the new dataset")
        parser.add_argument("contact_info", action="store", type=str, help="Contact information for the new dataset")
        parser.add_argument("project", action="store", type=str, help="Parent project identifier for the new dataset")
        parser.add_argument("data_use", action="store", type=str, help="Path to a data use JSON file for the dataset")

    def handle(self, *args, **options):
        data_use = None

        if options["data_use"] is not None:
            with open(options["data_use"], "r") as df:
                data_use = json.load(df)

        p = Dataset.objects.create(
            title=options["title"],
            description=options["description"],
            contact_info=options["contact_info"],
            project=Project.objects.get(identifier=options["project"].strip()),
            data_use=data_use,
        )

        print("Dataset created:", p)
