import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from chord_metadata_service.phenopackets.models import (
    HtsFile,
    Disease,
    Biosample,
    PhenotypicFeature,
    Phenopacket
)
from chord_metadata_service.phenopackets.indices import (
    build_htsfile_index,
    remove_htsfile_index,
    build_disease_index,
    remove_disease_index,
    build_biosample_index,
    remove_biosample_index,
    build_phenotypicfeature_index,
    remove_phenotypicfeature_index,
    build_phenopacket_index,
    remove_phenopacket_index
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@receiver(post_save, sender=HtsFile)
def index_htsfile(sender, instance, **kwargs):
    build_htsfile_index(instance)
    logging.info(f'index_htsfile_signal {instance.uri}')


@receiver(post_delete, sender=HtsFile)
def remove_htsfile(sender, instance, **kwargs):
    remove_htsfile_index(instance)
    logging.info(f'remove_htsfile_signal {instance.uri}')


@receiver(post_save, sender=Disease)
def index_disease(sender, instance, **kwargs):
    build_disease_index(instance)
    logging.info(f'index_htsfile_signal {instance.id}')


@receiver(post_delete, sender=Disease)
def remove_disease(sender, instance, **kwargs):
    remove_disease_index(instance)
    logging.info(f'remove_htsfile_signal {instance.id}')


@receiver(post_save, sender=Biosample)
def index_biosample(sender, instance, **kwargs):
    build_biosample_index(instance)
    logging.info(f'index_biosample_signal {instance.id}')


@receiver(post_delete, sender=Biosample)
def remove_biosample(sender, instance, **kwargs):
    remove_biosample_index(instance)
    logging.info(f'remove_biosample_signal {instance.id}')


@receiver(post_save, sender=PhenotypicFeature)
def index_phenotypicfeature(sender, instance, **kwargs):
    build_phenotypicfeature_index(instance)
    logging.info(f'index_phenotypicfeature_signal {instance.id}')


@receiver(post_delete, sender=PhenotypicFeature)
def remove_phenotypicfeature(sender, instance, **kwargs):
    remove_phenotypicfeature_index(instance)
    logging.info(f'remove_phenotypicfeature_signal {instance.id}')


@receiver(post_save, sender=Phenopacket)
def index_phenopacket(sender, instance, **kwargs):
    build_phenopacket_index(instance)
    logging.info(f'index_phenopacket_signal {instance.id}')


@receiver(post_delete, sender=Phenopacket)
def remove_phenopacket(sender, instance, **kwargs):
    remove_phenopacket_index(instance)
    logging.info(f'remove_phenopacket_signal {instance.id}')
