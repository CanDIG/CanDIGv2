from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField, ArrayField
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.resources.models import Resource
from chord_metadata_service.restapi.description_utils import rec_help
from chord_metadata_service.restapi.models import IndexableMixin
from chord_metadata_service.restapi.schema_utils import schema_list
from chord_metadata_service.restapi.validators import (
    JsonSchemaValidator,
    age_or_age_range_validator,
    ontology_validator,
    ontology_list_validator
)
from . import descriptions as d
from .schemas import (
    ALLELE_SCHEMA,
    PHENOPACKET_DISEASE_ONSET_SCHEMA,
    PHENOPACKET_EVIDENCE_SCHEMA,
    PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA,
    PHENOPACKET_UPDATE_SCHEMA,
)


#############################################################
#                                                           #
#                        Metadata                           #
#                                                           #
#############################################################


class MetaData(models.Model):
    """
    Class to store structured definitions of the resources
    and ontologies used within the phenopacket

    FHIR: Metadata
    """

    created = models.DateTimeField(default=timezone.now, help_text=rec_help(d.META_DATA, "created"))
    created_by = models.CharField(max_length=200, help_text=rec_help(d.META_DATA, "created_by"))
    submitted_by = models.CharField(max_length=200, blank=True, help_text=rec_help(d.META_DATA, "submitted_by"))
    resources = models.ManyToManyField(Resource, help_text=rec_help(d.META_DATA, "resources"))
    updates = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(
                        schema=schema_list(PHENOPACKET_UPDATE_SCHEMA), formats=['date-time'])],
                        help_text=rec_help(d.META_DATA, "updates"))
    phenopacket_schema_version = models.CharField(max_length=200, blank=True,
                                                  help_text='Schema version of the current phenopacket.')
    external_references = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(
                                    schema=schema_list(PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA))],
                                    help_text=rec_help(d.META_DATA, "external_references"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.META_DATA, "extra_properties"))
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


#############################################################


#############################################################
#                                                           #
#                  Phenotypic information                   #
#                                                           #
#############################################################


class PhenotypicFeature(models.Model, IndexableMixin):
    """
    Class to describe a phenotype of an Individual

    FHIR: Condition or Observation
    """

    description = models.CharField(max_length=200, blank=True, help_text=rec_help(d.PHENOTYPIC_FEATURE, "description"))
    pftype = JSONField(verbose_name='type', validators=[ontology_validator],
                       help_text=rec_help(d.PHENOTYPIC_FEATURE, "type"))
    negated = models.BooleanField(default=False, help_text=rec_help(d.PHENOTYPIC_FEATURE, "negated"))
    severity = JSONField(blank=True, null=True, validators=[ontology_validator],
                         help_text=rec_help(d.PHENOTYPIC_FEATURE, "severity"))
    modifier = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                         help_text=rec_help(d.PHENOTYPIC_FEATURE, "modifier"))
    onset = JSONField(blank=True, null=True, validators=[ontology_validator],
                      help_text=rec_help(d.PHENOTYPIC_FEATURE, "onset"))
    # evidence can stay here because evidence is given for an observation of PF
    # JSON schema to check evidence_code is present
    # FHIR: Condition.evidence
    evidence = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(schema=PHENOPACKET_EVIDENCE_SCHEMA)],
                         help_text=rec_help(d.PHENOTYPIC_FEATURE, "evidence"))
    biosample = models.ForeignKey(
        "Biosample", on_delete=models.SET_NULL, blank=True, null=True, related_name='phenotypic_features')
    phenopacket = models.ForeignKey(
        "Phenopacket", on_delete=models.SET_NULL, blank=True, null=True, related_name='phenotypic_features')
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.PHENOTYPIC_FEATURE, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class Procedure(models.Model):
    """
    Class to represent a clinical procedure performed on an individual
    (subject) in order to extract a biosample

    FHIR: Procedure
    """

    code = JSONField(validators=[ontology_validator], help_text=rec_help(d.PROCEDURE, "code"))
    body_site = JSONField(blank=True, null=True, validators=[ontology_validator],
                          help_text=rec_help(d.PROCEDURE, "body_site"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.PROCEDURE, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class HtsFile(models.Model, IndexableMixin):
    """
    Class to link HTC files with data

    FHIR: DocumentReference
    """

    HTS_FORMAT = (
        ('UNKNOWN', 'UNKNOWN'),
        ('SAM', 'SAM'),
        ('BAM', 'BAM'),
        ('CRAM', 'CRAM'),
        ('VCF', 'VCF'),
        ('BCF', 'BCF'),
        ('GVCF', 'GVCF'),
    )
    uri = models.URLField(primary_key=True, max_length=200, help_text=rec_help(d.HTS_FILE, "uri"))
    description = models.CharField(max_length=200, blank=True, help_text=rec_help(d.HTS_FILE, "description"))
    hts_format = models.CharField(max_length=200, choices=HTS_FORMAT, help_text=rec_help(d.HTS_FILE, "hts_format"))
    genome_assembly = models.CharField(max_length=200, help_text=rec_help(d.HTS_FILE, "genome_assembly"))
    # e.g.
    # "individualToSampleIdentifiers": {
    #   "patient23456": "NA12345"
    # TODO how to perform this validation, ensure the patient id is the correct one?
    individual_to_sample_identifiers = JSONField(
        blank=True, null=True, help_text=rec_help(d.HTS_FILE, "individual_to_sample_identifiers"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.HTS_FILE, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.uri)


class Gene(models.Model):
    """
    Class to represent an identifier for a gene

    FHIR: ?
    Draft extension for Gene is in development
    where Gene defined via class CodeableConcept
    """

    # Gene id is unique
    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.GENE, "id"))
    # CURIE style? Yes!
    alternate_ids = ArrayField(models.CharField(max_length=200, blank=True), blank=True, default=list,
                               help_text=rec_help(d.GENE, "alternate_ids"))
    symbol = models.CharField(max_length=200, help_text=rec_help(d.GENE, "symbol"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.GENE, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class Variant(models.Model):
    """
    Class to describe Individual variants or diagnosed causative variants

    FHIR: Observation ?
    Draft extension for Variant is in development
    """

    ALLELE = (
        ('hgvsAllele', 'hgvsAllele'),
        ('vcfAllele', 'vcfAllele'),
        ('spdiAllele', 'spdiAllele'),
        ('iscnAllele', 'iscnAllele'),
    )
    allele_type = models.CharField(max_length=200, choices=ALLELE, help_text="One of four allele types.")
    allele = JSONField(validators=[JsonSchemaValidator(schema=ALLELE_SCHEMA)],
                       help_text=rec_help(d.VARIANT, "allele"))
    zygosity = JSONField(blank=True, null=True, validators=[ontology_validator],
                         help_text=rec_help(d.VARIANT, "zygosity"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.VARIANT, "extra_properties"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Disease(models.Model, IndexableMixin):
    """
    Class to represent a diagnosis and inference or hypothesis about the cause
    underlying the observed phenotypic abnormalities

    FHIR: Condition
    """

    term = JSONField(validators=[ontology_validator], help_text=rec_help(d.DISEASE, "term"))
    # "ageOfOnset": {
    # "age": "P38Y7M"
    # }
    # OR
    # "ageOfOnset": {
    # "id": "HP:0003581",
    # "label": "Adult onset"
    # }
    onset = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(schema=PHENOPACKET_DISEASE_ONSET_SCHEMA)],
                      help_text=rec_help(d.DISEASE, "onset"))
    disease_stage = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                              help_text=rec_help(d.DISEASE, "disease_stage"))
    tnm_finding = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                            help_text=rec_help(d.DISEASE, "tnm_finding"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.DISEASE, "extra_properties"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Biosample(models.Model, IndexableMixin):
    """
    Class to describe a unit of biological material

    FHIR: Specimen
    """

    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.BIOSAMPLE, "id"))
    # if Individual instance is deleted Biosample instance is deleted too
    individual = models.ForeignKey(
        Individual, on_delete=models.CASCADE, blank=True, null=True, related_name="biosamples",
        help_text=rec_help(d.BIOSAMPLE, "individual_id"))
    description = models.CharField(max_length=200, blank=True, help_text=rec_help(d.BIOSAMPLE, "description"))
    sampled_tissue = JSONField(validators=[ontology_validator], help_text=rec_help(d.BIOSAMPLE, "sampled_tissue"))
    # phenotypic_features = models.ManyToManyField(PhenotypicFeature, blank=True,
    #   help_text='List of phenotypic abnormalities of the sample.')
    taxonomy = JSONField(blank=True, null=True, validators=[ontology_validator],
                         help_text=rec_help(d.BIOSAMPLE, "taxonomy"))
    # An ISO8601 string represent age
    individual_age_at_collection = JSONField(blank=True, null=True, validators=[age_or_age_range_validator],
                                             help_text=rec_help("individual_age_at_collection"))
    histological_diagnosis = JSONField(
        blank=True, null=True, validators=[ontology_validator],
        help_text=rec_help(d.BIOSAMPLE, "histological_diagnosis"))
    # TODO: Lists?
    tumor_progression = JSONField(blank=True, null=True, validators=[ontology_validator],
                                  help_text=rec_help(d.BIOSAMPLE, "tumor_progression"))
    tumor_grade = JSONField(blank=True, null=True, validators=[ontology_validator],
                            help_text=rec_help(d.BIOSAMPLE, "tumor_grade"))
    diagnostic_markers = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                                   help_text=rec_help(d.BIOSAMPLE, "diagnostic_markers"))
    # CHECK! if Procedure instance is deleted Biosample instance is deleted too
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, help_text=rec_help(d.BIOSAMPLE, "procedure"))
    hts_files = models.ManyToManyField(
        HtsFile, blank=True, related_name='biosample_hts_files', help_text=rec_help(d.BIOSAMPLE, "hts_files"))
    variants = models.ManyToManyField(Variant, blank=True, help_text=rec_help(d.BIOSAMPLE, "variants"))
    is_control_sample = models.BooleanField(default=False, help_text=rec_help(d.BIOSAMPLE, "is_control_sample"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.BIOSAMPLE, "extra_properties"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_sample_tissue_data(self):
        return {'reference': {
            'reference': self.sampled_tissue.get('id'),
            'display': self.sampled_tissue.get('label')
            }
        }


class Phenopacket(models.Model, IndexableMixin):
    """
    Class to aggregate Individual's experiments data

    FHIR: Composition
    """

    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.PHENOPACKET, "id"))
    # if Individual instance is deleted Phenopacket instance is deleted too
    # CHECK !!! Force as required?
    subject = models.ForeignKey(
        Individual, on_delete=models.CASCADE, related_name="phenopackets",
        help_text=rec_help(d.PHENOPACKET, "subject"))
    # PhenotypicFeatures are present in Biosample, so can be accessed via Biosample instance
    # phenotypic_features = models.ManyToManyField(PhenotypicFeature, blank=True,
    #   help_text='Phenotypic features observed in the proband.')
    biosamples = models.ManyToManyField(Biosample, blank=True, help_text=rec_help(d.PHENOPACKET, "biosamples"))
    genes = models.ManyToManyField(Gene, blank=True, help_text=rec_help(d.PHENOPACKET, "genes"))
    variants = models.ManyToManyField(Variant, blank=True, help_text=rec_help(d.PHENOPACKET, "variants"))
    diseases = models.ManyToManyField(Disease, blank=True, help_text=rec_help(d.PHENOPACKET, "diseases"))
    hts_files = models.ManyToManyField(HtsFile, blank=True, help_text=rec_help(d.PHENOPACKET, "hts_files"))
    # TODO OneToOneField
    meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE, help_text=rec_help(d.PHENOPACKET, "meta_data"))
    table = models.ForeignKey("chord.Table", on_delete=models.CASCADE, blank=True, null=True)  # TODO: Help text
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.PHENOPACKET, "extra_properties"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


#############################################################
#                                                           #
#                    Interpretation                         #
#                                                           #
#############################################################


class GenomicInterpretation(models.Model):
    """
    Class to represent a statement about the contribution
    of a genomic element towards the observed phenotype

    FHIR: Observation
    """

    GENOMIC_INTERPRETATION_STATUS = (
        ('UNKNOWN', 'UNKNOWN'),
        ('REJECTED', 'REJECTED'),
        ('CANDIDATE', 'CANDIDATE'),
        ('CAUSATIVE', 'CAUSATIVE')
        )
    status = models.CharField(max_length=200, choices=GENOMIC_INTERPRETATION_STATUS,
                              help_text='How the call of this GenomicInterpretation was interpreted.')
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE,
                             blank=True, null=True, help_text='The gene contributing to the diagnosis.')
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE,
                                blank=True, null=True, help_text='The variant contributing to the diagnosis.')
    extra_properties = JSONField(blank=True, null=True,
                                 help_text='Extra properties that are not supported by current schema')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def clean(self):
        if not (self.gene or self.variant):
            raise ValidationError('Either Gene or Variant must be specified')

    def __str__(self):
        return str(self.id)


class Diagnosis(models.Model):
    """
    Class to refer to disease that is present in the individual analyzed

    FHIR: Condition
    """

    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, help_text='The diagnosed condition.')
    # required?
    genomic_interpretations = models.ManyToManyField(
        GenomicInterpretation, blank=True,
        help_text='The genomic elements assessed as being responsible for the disease.')
    extra_properties = JSONField(blank=True, null=True,
                                 help_text='Extra properties that are not supported by current schema')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class Interpretation(models.Model):
    """
    Class to represent the interpretation of a genomic analysis

    FHIR: DiagnosticReport
    """

    RESOLUTION_STATUS = (
        ('UNKNOWN', 'UNKNOWN'),
        ('SOLVED', 'SOLVED'),
        ('UNSOLVED', 'UNSOLVED'),
        ('IN_PROGRESS', 'IN_PROGRESS')
    )

    id = models.CharField(primary_key=True, max_length=200, help_text='An arbitrary identifier for the interpretation.')
    resolution_status = models.CharField(choices=RESOLUTION_STATUS, max_length=200, blank=True,
                                         help_text='The current status of work on the case.')
    # In Phenopackets schema this field is 'phenopacket_or_family'
    phenopacket = models.ForeignKey(Phenopacket, on_delete=models.CASCADE, related_name='interpretations',
                                    help_text='The subject of this interpretation.')
    # fetch disease via from phenopacket
    # diagnosis on one disease ? there can be many disease associated with phenopacket
    diagnosis = models.ManyToManyField(Diagnosis, help_text='One or more diagnoses, if made.')
    meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE, help_text='Metadata about this interpretation.')
    extra_properties = JSONField(blank=True, null=True,
                                 help_text='Extra properties that are not supported by current schema')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
