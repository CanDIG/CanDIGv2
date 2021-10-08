from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.db import models

from chord_metadata_service.restapi.description_utils import rec_help

from . import descriptions as d


class Resource(models.Model):
    """
    Class to represent a description of an external resource
    used for referencing an object

    FHIR: CodeSystem
    """

    class Meta:
        unique_together = (("namespace_prefix", "version"),)

    # resource_id e.g. "id": "uniprot:2019_07"
    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.RESOURCE, "id"))
    name = models.CharField(max_length=200, help_text=rec_help(d.RESOURCE, "name"))
    namespace_prefix = models.CharField(max_length=200, help_text=rec_help(d.RESOURCE, "namespace_prefix"))
    url = models.URLField(max_length=200, help_text=rec_help(d.RESOURCE, "url"))
    version = models.CharField(max_length=200, help_text=rec_help(d.RESOURCE, "version"))
    iri_prefix = models.URLField(max_length=200, help_text=rec_help(d.RESOURCE, "iri_prefix"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.RESOURCE, "extra_properties"))

    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # For phenopackets compliance, we need to have a string identifier. Django does not allow compound keys, we
        # ideally want to identify resources by the pair (namespace_prefix, version). In this case, we hack this by
        # enforcing that id == (namespace_prefix, version). In the case of an unspecified version, enforce
        # id == namespace_prefix.
        if (self.version and self.id != f"{self.namespace_prefix}:{self.version}") or \
                (not self.version and self.id != self.namespace_prefix):
            raise ValidationError({
                "id": [ValidationError("Resource ID must match the format 'namespace_prefix:version'")],
            })

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)
