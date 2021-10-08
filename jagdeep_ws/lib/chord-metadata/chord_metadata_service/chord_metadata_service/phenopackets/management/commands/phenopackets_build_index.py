import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from chord_metadata_service.phenopackets.models import (
    HtsFile,
    Disease,
    Biosample,
    PhenotypicFeature,
    Phenopacket
)
from chord_metadata_service.phenopackets.indices import (
    build_htsfile_index,
    build_disease_index,
    build_biosample_index,
    build_phenotypicfeature_index,
    build_phenopacket_index
)
from chord_metadata_service.metadata.elastic import es


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    help = """
        Takes every phenopacket-related data in the DB, port them over
        to FHIR-compliant JSON and upload them into elasticsearch
    """

    def handle(self, *args, **options):
        # TODO: currently only place we create the index, will have to review
        if es:
            es.indices.create(index=settings.FHIR_INDEX_NAME, ignore=400)

            htsfiles = HtsFile.objects.all()

            for htsfile in htsfiles:
                created_or_updated = build_htsfile_index(htsfile)
                logger.info(f"{created_or_updated} index for htsfile ID {htsfile.uri} indexed id {htsfile.index_id}")

            diseases = Disease.objects.all()

            for disease in diseases:
                created_or_updated = build_disease_index(disease)
                logger.info(f"{created_or_updated} index for disease ID {disease.id} indexed id {disease.index_id}")

            biosamples = Biosample.objects.all()

            for biosample in biosamples:
                created_or_updated = build_biosample_index(biosample)
                logger.info(f"{created_or_updated} index for biosample ID {biosample.id} indexed id "
                            f"{biosample.index_id}")

            features = PhenotypicFeature.objects.all()

            for feature in features:
                created_or_updated = build_phenotypicfeature_index(feature)
                logger.info(f"{created_or_updated} index for phenotypic feature ID {feature.index_id} indexed ID "
                            f"{feature.index_id}")

            phenopackets = Phenopacket.objects.all()

            for phenopacket in phenopackets:
                created_or_updated = build_phenopacket_index(phenopacket)
                logger.info(f"{created_or_updated} index for phenopacket ID {phenopacket.id} indexed ID "
                            f"{phenopacket.index_id}")
        else:
            logger.error("No connection to elasticsearch")
