from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from chord_metadata_service.restapi.models import IndexableMixin
from chord_metadata_service.restapi.validators import ontology_validator, age_or_age_range_validator
from .validators import comorbid_condition_validator


class Individual(models.Model, IndexableMixin):
    """ Class to store demographic information about an Individual (Patient) """

    SEX = (
        ('UNKNOWN_SEX', 'UNKNOWN_SEX'),
        ('FEMALE', 'FEMALE'),
        ('MALE', 'MALE'),
        ('OTHER_SEX', 'OTHER_SEX')
    )

    KARYOTYPIC_SEX = (
        ('UNKNOWN_KARYOTYPE', 'UNKNOWN_KARYOTYPE'),
        ('XX', 'XX'),
        ('XY', 'XY'),
        ('XO', 'XO'),
        ('XXY', 'XXY'),
        ('XXX', 'XXX'),
        ('XXYY', 'XXYY'),
        ('XXXY', 'XXXY'),
        ('XXXX', 'XXXX'),
        ('XYY', 'XYY'),
        ('OTHER_KARYOTYPE', 'OTHER_KARYOTYPE'),
    )

    id = models.CharField(primary_key=True, max_length=200, help_text='An arbitrary identifier for the individual.')
    # TODO check for CURIE
    alternate_ids = ArrayField(models.CharField(max_length=200), blank=True, null=True,
                               help_text='A list of alternative identifiers for the individual.')
    date_of_birth = models.DateField(null=True, blank=True, help_text='A timestamp either exact or imprecise.')
    # An ISO8601 string represent age
    age = JSONField(blank=True, null=True, validators=[age_or_age_range_validator],
                    help_text='The age or age range of the individual.')
    sex = models.CharField(choices=SEX, max_length=200,  blank=True, null=True,
                           help_text='Observed apparent sex of the individual.')
    karyotypic_sex = models.CharField(choices=KARYOTYPIC_SEX, max_length=200, default='UNKNOWN_KARYOTYPE',
                                      help_text='The karyotypic sex of the individual.')
    taxonomy = JSONField(blank=True, null=True, validators=[ontology_validator],
                         help_text='Ontology resource representing the species (e.g., NCBITaxon:9615).')
    # FHIR specific
    active = models.BooleanField(default=False, help_text='Whether this patient\'s record is in active use.')
    deceased = models.BooleanField(default=False, help_text='Indicates if the individual is deceased or not.')
    # mCode specific
    # this field should be complex Ontology - clinical status and code - two Codeable concept - single, cl status has
    # enum list of values
    # TODO add these fields to FHIR converter ?
    comorbid_condition = JSONField(blank=True, null=True, validators=[comorbid_condition_validator],
                                   help_text='One or more conditions that occur with primary condition.')
    # TODO decide use ONTOLOGY_CLASS vs. CODEABLE_CONCEPT - currently Ontology class
    ecog_performance_status = JSONField(blank=True, null=True, validators=[ontology_validator],
                                        help_text='Value representing the Eastern Cooperative '
                                                  'Oncology Group performance status.')
    karnofsky = JSONField(blank=True, null=True, validators=[ontology_validator],
                          help_text='Value representing the Karnofsky Performance status.')
    race = models.CharField(max_length=200, blank=True, help_text='A code for the person\'s race.')
    ethnicity = models.CharField(max_length=200, blank=True, help_text='A code for the person\'s ethnicity.')
    # extra
    extra_properties = JSONField(blank=True, null=True,
                                 help_text='Extra properties that are not supported by current schema')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
