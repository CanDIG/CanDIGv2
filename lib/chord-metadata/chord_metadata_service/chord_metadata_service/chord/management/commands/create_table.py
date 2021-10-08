import uuid

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET
from chord_metadata_service.chord.models import Dataset, TableOwnership, Table


class Command(BaseCommand):
    help = """
        Creates a Katsu/Bento table in the database.
        Arguments: "name" (experiment|phenopacket) "dataset"
    """

    def add_arguments(self, parser):
        parser.add_argument("name", action="store", type=str, help="The name for the new table")
        parser.add_argument("data_type", action="store", choices=[DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET],
                            type=str, help="The data type of this new table (experiment|phenopacket)")
        parser.add_argument("dataset", action="store", type=str, help="Parent dataset identifier for the new table")

    def handle(self, *args, **options):
        with transaction.atomic():
            to = TableOwnership.objects.create(
                table_id=str(uuid.uuid4()),
                service_id=settings.CHORD_SERVICE_ID,
                service_artifact=settings.CHORD_SERVICE_ARTIFACT,
                dataset=Dataset.objects.get(identifier=options["dataset"]),
            )

            print("Table ownership created:", to)

            t = Table.objects.create(
                ownership_record=to,
                name=options["name"],
                data_type=options["data_type"],
            )

            print("Table created:", t)
