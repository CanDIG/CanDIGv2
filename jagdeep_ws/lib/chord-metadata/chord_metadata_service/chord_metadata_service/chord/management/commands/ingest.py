from django.core.management.base import BaseCommand
from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET
from chord_metadata_service.chord.ingest import ingest_experiments_workflow, ingest_phenopacket_workflow
from chord_metadata_service.chord.models import Table


class Command(BaseCommand):
    help = """
        Ingests a JSON file into a Katsu/Bento table.
        Arguments: "table" ./path/to/data.json
    """

    def add_arguments(self, parser):
        parser.add_argument("table", action="store", type=str, help="The table ID to ingest into")
        parser.add_argument("data", action="store", type=str, help="JSON data file to ingest")

    def handle(self, *args, **options):
        t = Table.objects.get(ownership_record_id=options["table"])

        {
            DATA_TYPE_EXPERIMENT: ingest_experiments_workflow,
            DATA_TYPE_PHENOPACKET: ingest_phenopacket_workflow,
        }[t.data_type]({"json_document": options["data"]}, options["table"])

        print("Ingested data successfully.")
