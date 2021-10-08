import collections
import uuid

from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.resources.models import Resource

from .data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET


__all__ = ["Project", "Dataset", "TableOwnership", "Table"]


def version_default():
    return f"version_{timezone.now()}"


#############################################################
#                                                           #
#                   Project Management                      #
#                                                           #
#############################################################

class Project(models.Model):
    """
    Class to represent a Project, which contains multiple
    Datasets which are each a group of Phenopackets.
    """

    identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (ID: {self.identifier})"


class Dataset(models.Model):
    """
    Class to represent a Dataset, which contains multiple Phenopackets.
    """

    identifier = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    contact_info = models.TextField(blank=True)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,  # Delete dataset upon project deletion
        related_name="datasets"
    )

    data_use = JSONField()
    linked_field_sets = JSONField(blank=True, default=list, help_text="Data type fields which are linked together.")

    additional_resources = models.ManyToManyField(Resource, blank=True, help_text="Any resource objects linked to this "
                                                                                  "dataset that aren't specified by a "
                                                                                  "phenopacket in the dataset.")

    @property
    def resources(self):
        # Union of phenopacket resources and any additional resources for other table types
        return Resource.objects.filter(id__in={
            *(r.id for r in self.additional_resources.all()),
            *(
                r.id
                for p in Phenopacket.objects.filter(
                    table_id__in={t.table_id for t in self.table_ownership.all()}
                ).prefetch_related("meta_data", "meta_data__resources")
                for r in p.meta_data.resources.all()
            ),
        })

    @property
    def n_of_tables(self):
        return TableOwnership.objects.filter(dataset=self).count()

    # --------------------------- DATS model fields ---------------------------

    alternate_identifiers = JSONField(blank=True, default=list, help_text="Alternate identifiers for the dataset.")
    related_identifiers = JSONField(blank=True, default=list, help_text="Related identifiers for the dataset.")
    dates = JSONField(blank=True, default=list, help_text="Relevant dates for the datasets, a date must be added, e.g. "
                                                          "creation date or last modification date should be added.")
    # TODO: Can this be auto-synthesized? (Specified in settings)
    stored_in = JSONField(blank=True, null=True, help_text="The data repository hosting the dataset.")
    spatial_coverage = JSONField(blank=True, default=list, help_text="The geographical extension and span covered "
                                                                     "by the dataset and its measured "
                                                                     "dimensions/variables.")
    types = JSONField(blank=True, default=list, help_text="A term, ideally from a controlled terminology, identifying "
                                                          "the dataset type or nature of the data, placing it in a "
                                                          "typology.")
    # TODO: Can this be derived from / combined with DUO stuff?
    availability = models.CharField(max_length=200, blank=True,
                                    help_text="A qualifier indicating the different types of availability for a "
                                              "dataset (available, unavailable, embargoed, available with restriction, "
                                              "information not available).")
    refinement = models.CharField(max_length=200, blank=True,
                                  help_text="A qualifier to describe the level of data processing of the dataset and "
                                            "its distributions.")
    aggregation = models.CharField(max_length=200, blank=True,
                                   help_text="A qualifier indicating if the entity represents an 'instance of dataset' "
                                             "or a 'collection of datasets'.")
    privacy = models.CharField(max_length=200, blank=True,
                               help_text="A qualifier to describe the data protection applied to the dataset. This is "
                                         "relevant for clinical data.")
    distributions = JSONField(blank=True, default=list, help_text="The distribution(s) by which datasets are made "
                                                                  "available (for example: mySQL dump).")
    dimensions = JSONField(blank=True, default=list, help_text="The different dimensions (granular components) "
                                                               "making up a dataset.")
    primary_publications = JSONField(blank=True, default=list, help_text="The primary publication(s) associated with "
                                                                         "the dataset, usually describing how the "
                                                                         "dataset was produced.")
    citations = JSONField(blank=True, default=list, help_text="The publication(s) that cite this dataset.")
    citation_count = models.IntegerField(blank=True, null=True,
                                         help_text="The number of publications that cite this dataset (enumerated in "
                                                   "the citations property).")
    produced_by = JSONField(blank=True, null=True, help_text="A study process which generated a given dataset, if any.")
    creators = JSONField(blank=True, default=list, help_text="The person(s) or organization(s) which contributed to "
                                                             "the creation of the dataset.")
    # TODO: How to reconcile this and data_use?
    licenses = JSONField(blank=True, default=list, help_text="The terms of use of the dataset.")
    # is_about this field will be calculated based on sample field
    # in tableOwnership
    has_part = models.ManyToManyField("self", blank=True, help_text="A Dataset that is a subset of this Dataset; "
                                                                    "Datasets declaring the 'hasPart' relationship are "
                                                                    "considered a collection of Datasets, the "
                                                                    "aggregation criteria could be included in "
                                                                    "the 'description' field.")
    acknowledges = JSONField(blank=True, default=list, help_text="The grant(s) which funded and supported the work "
                                                                 "reported by the dataset.")
    keywords = JSONField(blank=True, default=list, help_text="Tags associated with the dataset, which will help in "
                                                             "its discovery.")
    version = models.CharField(max_length=200, blank=True, default=version_default,
                               help_text="A release point for the dataset when applicable.")
    extra_properties = JSONField(blank=True, null=True, help_text="Extra properties that do not fit in the previous "
                                                                  "specified attributes.")

    # -------------------------------------------------------------------------

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def clean(self):
        # Check that all namespace prefices are unique within a dataset
        c = collections.Counter(r.namespace_prefix for r in self.resources)
        mc = (*c.most_common(1), (None, 0))[0]
        if mc[1] > 1:
            raise ValidationError(f"Dataset {self.identifier} cannot have ambiguous resource namespace prefix {mc[0]}")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} (ID: {self.identifier})"


class TableOwnership(models.Model):
    """
    Class to represent a Table, which are organizationally part of a Dataset and can optionally be
    attached to a Phenopacket (and possibly a Biosample).
    """

    table_id = models.CharField(primary_key=True, max_length=200)
    service_id = models.CharField(max_length=200)
    service_artifact = models.CharField(max_length=200, default="")

    # Delete table ownership upon project/dataset deletion
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='table_ownership')

    def __str__(self):
        return f"{self.dataset} -> {self.table_id}"


class Table(models.Model):
    TABLE_DATA_TYPE_CHOICES = (
        (DATA_TYPE_EXPERIMENT, DATA_TYPE_EXPERIMENT),
        (DATA_TYPE_PHENOPACKET, DATA_TYPE_PHENOPACKET),
    )

    ownership_record = models.OneToOneField(TableOwnership, on_delete=models.CASCADE, primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    data_type = models.CharField(max_length=30, choices=TABLE_DATA_TYPE_CHOICES)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def identifier(self):
        return self.ownership_record_id

    @property
    def dataset(self):
        return self.ownership_record.dataset

    def __str__(self):
        return f"{self.name} (ID: {self.ownership_record.table_id}, Type: {self.data_type})"
