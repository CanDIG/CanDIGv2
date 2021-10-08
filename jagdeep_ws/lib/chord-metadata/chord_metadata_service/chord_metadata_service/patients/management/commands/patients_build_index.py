import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.patients.indices import build_individual_index
from chord_metadata_service.metadata.elastic import es


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = """
        Takes every individual in the DB, port them over to FHIR-compliant
        JSON and upload them into elasticsearch
    """

    def handle(self, *args, **options):
        # TODO: currently only place we create the index, will have to review
        if es:
            es.indices.create(index=settings.FHIR_INDEX_NAME, ignore=400)

            individuals = Individual.objects.all()

            for ind in individuals:
                created_or_updated = build_individual_index(ind)
                logger.info(f"{created_or_updated} index for patient ID {ind.id} indexed ID {ind.index_id}")
        else:
            logger.error("No connection to elasticsearch")
