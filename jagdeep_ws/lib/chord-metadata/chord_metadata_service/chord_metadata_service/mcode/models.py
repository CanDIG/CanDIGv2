from django.utils import timezone
from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from chord_metadata_service.restapi.models import IndexableMixin
from chord_metadata_service.phenopackets.models import Gene
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.restapi.description_utils import rec_help
import chord_metadata_service.mcode.descriptions as d
from chord_metadata_service.restapi.validators import ontology_validator, ontology_list_validator
from .validators import (
    tumor_marker_data_value_validator,
    complex_ontology_validator
)


class GeneticSpecimen(models.Model, IndexableMixin):
    """
    Class to describe a biosample used for genomics testing or analysis.
    """
    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.GENETIC_SPECIMEN, "id"))
    specimen_type = JSONField(validators=[ontology_validator], help_text=rec_help(d.GENETIC_SPECIMEN, "specimen_type"))
    collection_body = JSONField(blank=True, null=True, validators=[ontology_validator],
                                help_text=rec_help(d.GENETIC_SPECIMEN, "collection_body"))
    laterality = JSONField(blank=True, null=True, validators=[ontology_validator],
                           help_text=rec_help(d.GENETIC_SPECIMEN, "laterality"))
    extra_properties = JSONField(blank=True, null=True,
                                 help_text=rec_help(d.GENETIC_SPECIMEN, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.id)


class CancerGeneticVariant(models.Model, IndexableMixin):
    """
    Class to record an alteration in DNA.
    """
    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.CANCER_GENETIC_VARIANT, "id"))
    data_value = JSONField(blank=True, null=True, validators=[ontology_validator],
                           help_text=rec_help(d.CANCER_GENETIC_VARIANT, "data_value"))
    method = JSONField(blank=True, null=True, validators=[ontology_validator],
                       help_text=rec_help(d.CANCER_GENETIC_VARIANT, "method"))
    amino_acid_change = JSONField(blank=True, null=True, validators=[ontology_validator],
                                  help_text=rec_help(d.CANCER_GENETIC_VARIANT, "amino_acid_change"))
    amino_acid_change_type = JSONField(blank=True, null=True, validators=[ontology_validator],
                                       help_text=rec_help(d.CANCER_GENETIC_VARIANT, "amino_acid_change_type"))
    cytogenetic_location = JSONField(blank=True, null=True,
                                     help_text=rec_help(d.CANCER_GENETIC_VARIANT, "cytogenetic_location"))
    cytogenetic_nomenclature = JSONField(blank=True, null=True, validators=[ontology_validator],
                                         help_text=rec_help(d.CANCER_GENETIC_VARIANT, "cytogenetic_nomenclature"))
    gene_studied = models.ManyToManyField(Gene, blank=True,
                                          help_text=rec_help(d.CANCER_GENETIC_VARIANT, "gene_studied"))
    genomic_dna_change = JSONField(blank=True, null=True, validators=[ontology_validator],
                                   help_text=rec_help(d.CANCER_GENETIC_VARIANT, "genomic_dna_change"))
    genomic_source_class = JSONField(blank=True, null=True, validators=[ontology_validator],
                                     help_text=rec_help(d.CANCER_GENETIC_VARIANT, "genomic_source_class"))
    variation_code = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                               help_text=rec_help(d.CANCER_GENETIC_VARIANT, "variation_code"))
    extra_properties = JSONField(blank=True, null=True,
                                 help_text=rec_help(d.CANCER_GENETIC_VARIANT, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.id)


class GenomicRegionStudied(models.Model, IndexableMixin):
    """
    Class to describe the area of the genome region referenced in testing for variants.
    """
    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.GENOMIC_REGION_STUDIED, "id"))
    # TODO schema Range list
    dna_ranges_examined = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                                    help_text=rec_help(d.GENOMIC_REGION_STUDIED, "dna_ranges_examined"))
    dna_region_description = ArrayField(models.CharField(max_length=100,
                                                         help_text=rec_help(d.GENOMIC_REGION_STUDIED,
                                                                            'dna_region_description')),
                                        blank=True, default=list)
    gene_mutation = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                              help_text=rec_help(d.GENOMIC_REGION_STUDIED, "gene_mutation"))
    # TODO check: thisis not a Reference in mcode data dictionary why not?
    gene_studied = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                             help_text=rec_help(d.GENOMIC_REGION_STUDIED, "gene_studied"))
    genomic_reference_sequence_id = JSONField(blank=True, null=True,
                                              help_text=rec_help(d.GENOMIC_REGION_STUDIED,
                                                                 "genomic_reference_sequence_id"))
    genomic_region_coordinate_system = JSONField(blank=True, null=True, validators=[ontology_validator],
                                                 help_text=rec_help(d.GENOMIC_REGION_STUDIED,
                                                                    "genomic_region_coordinate_system"))
    extra_properties = JSONField(blank=True, null=True,
                                 help_text=rec_help(d.GENOMIC_REGION_STUDIED, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.id)


class GenomicsReport(models.Model, IndexableMixin):
    """
    Genetic Analysis Summary.
    """

    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.GENOMICS_REPORT, "id"))
    code = JSONField(validators=[ontology_validator], help_text=rec_help(d.GENOMICS_REPORT, "code"))
    performing_organization_name = models.CharField(
        max_length=200, blank=True, help_text=rec_help(d.GENOMICS_REPORT, "performing_organization_name"))
    issued = models.DateTimeField(default=timezone.now, help_text=rec_help(d.GENOMICS_REPORT, "issued"))
    genetic_specimen = models.ManyToManyField(GeneticSpecimen, blank=True,
                                              help_text=rec_help(d.GENOMICS_REPORT, "genetic_specimen"))
    genetic_variant = models.ForeignKey(CancerGeneticVariant, blank=True, null=True, on_delete=models.SET_NULL,
                                        help_text=rec_help(d.GENOMICS_REPORT, "genetic_variant"))
    genomic_region_studied = models.ForeignKey(GenomicRegionStudied, blank=True, null=True, on_delete=models.SET_NULL,
                                               help_text=rec_help(d.GENOMICS_REPORT, "genomic_region_studied"))
    extra_properties = JSONField(blank=True, null=True,
                                 help_text=rec_help(d.GENOMICS_REPORT, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.id)


# ================================ Labs/Vital ================================


class LabsVital(models.Model, IndexableMixin):
    """
    Class  to record tests performed on patient.
    """
    # TODO Should this class be a part of Patients app? patient related metadata
    id = models.CharField(primary_key=True, max_length=200,
                          help_text=rec_help(d.LABS_VITAL, "id"))
    individual = models.ForeignKey(Individual, on_delete=models.CASCADE,
                                   help_text=rec_help(d.LABS_VITAL, "individual"))
    # TODO Change CodeableConcept to Ontology class
    tumor_marker_code = JSONField(validators=[ontology_validator],
                                  help_text=rec_help(d.LABS_VITAL, "tumor_marker_code"))
    tumor_marker_data_value = JSONField(blank=True, null=True, validators=[tumor_marker_data_value_validator],
                                        help_text=rec_help(d.LABS_VITAL, "tumor_marker_data_value"))
    extra_properties = JSONField(blank=True, null=True,
                                 help_text=rec_help(d.LABS_VITAL, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.id)


# ================================== Disease ==================================

class CancerCondition(models.Model, IndexableMixin):
    """
    Class to record the history of primary or secondary cancer conditions.
    """
    CANCER_CONDITION_TYPE = (
        ('primary', 'primary'),
        ('secondary', 'secondary')
    )
    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.CANCER_CONDITION, "id"))
    condition_type = models.CharField(choices=CANCER_CONDITION_TYPE, max_length=200,
                                      help_text=rec_help(d.CANCER_CONDITION, "condition_type"))
    body_site = JSONField(null=True, validators=[ontology_list_validator],
                          help_text=rec_help(d.CANCER_CONDITION, 'body_site'))
    laterality = JSONField(blank=True, null=True, validators=[ontology_validator],
                           help_text=rec_help(d.CANCER_CONDITION, "laterality"))
    clinical_status = JSONField(blank=True, null=True, validators=[ontology_validator],
                                help_text=rec_help(d.CANCER_CONDITION, "clinical_status"))
    code = JSONField(validators=[ontology_validator],
                     help_text=rec_help(d.CANCER_CONDITION, "code"))
    date_of_diagnosis = models.DateTimeField(blank=True, null=True,
                                             help_text=rec_help(d.CANCER_CONDITION, "date_of_diagnosis"))
    histology_morphology_behavior = JSONField(blank=True, null=True, validators=[ontology_validator],
                                              help_text=rec_help(d.CANCER_CONDITION, "histology_morphology_behavior"))
    verification_status = JSONField(blank=True, null=True, validators=[ontology_validator],
                                    help_text=rec_help(d.CANCER_CONDITION, "verification_status"))
    extra_properties = JSONField(blank=True, null=True,
                                 help_text=rec_help(d.CANCER_CONDITION, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.id)


class TNMStaging(models.Model, IndexableMixin):
    """
    Class to describe the spread of cancer in a patient’s body.
    """

    TNM_TYPES = (
        ('clinical', 'clinical'),
        ('pathologic', 'pathologic')
    )
    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.TNM_STAGING, "id"))
    tnm_type = models.CharField(choices=TNM_TYPES, max_length=200, help_text=rec_help(d.TNM_STAGING, "tnm_type"))
    stage_group = JSONField(validators=[complex_ontology_validator], help_text=rec_help(d.TNM_STAGING, "stage_group"))
    primary_tumor_category = JSONField(validators=[complex_ontology_validator],
                                       help_text=rec_help(d.TNM_STAGING, "primary_tumor_category"))
    regional_nodes_category = JSONField(validators=[complex_ontology_validator],
                                        help_text=rec_help(d.TNM_STAGING, "regional_nodes_category"))
    distant_metastases_category = JSONField(validators=[complex_ontology_validator],
                                            help_text=rec_help(d.TNM_STAGING, "distant_metastases_category"))
    # TODO check if one cancer condition has many TNM Staging
    cancer_condition = models.ForeignKey(CancerCondition, on_delete=models.CASCADE,
                                         help_text=rec_help(d.TNM_STAGING, "cancer_condition"))
    extra_properties = JSONField(blank=True, null=True,
                                 help_text=rec_help(d.TNM_STAGING, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.id)


# ================================= Treatment =================================

# ==== Procedure ====

class CancerRelatedProcedure(models.Model, IndexableMixin):
    """
    Class to represent radiological treatment or surgical action addressing a cancer condition.
    """

    PROCEDURE_TYPES = (
        ('radiation', 'radiation'),
        ('surgical', 'surgical')
    )
    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.CANCER_RELATED_PROCEDURE, "id"))
    procedure_type = models.CharField(choices=PROCEDURE_TYPES, max_length=200,
                                      help_text=rec_help(d.CANCER_RELATED_PROCEDURE, "procedure_type"))
    code = JSONField(validators=[ontology_validator], help_text=rec_help(d.CANCER_RELATED_PROCEDURE, "code"))
    body_site = JSONField(null=True, validators=[ontology_list_validator],
                          help_text=rec_help(d.CANCER_RELATED_PROCEDURE, 'body_site'))
    laterality = JSONField(blank=True, null=True, validators=[ontology_validator],
                           help_text=rec_help(d.CANCER_RELATED_PROCEDURE, "laterality"))
    treatment_intent = JSONField(blank=True, null=True, validators=[ontology_validator],
                                 help_text=rec_help(d.CANCER_RELATED_PROCEDURE, "treatment_intent"))
    # Only for Surgical Procedure
    # TODO CHANGE to ontology list validator
    reason_code = JSONField(blank=True, null=True, validators=[ontology_validator],
                            help_text=rec_help(d.CANCER_RELATED_PROCEDURE, "reason_code"))
    reason_reference = models.ManyToManyField(CancerCondition, blank=True,
                                              help_text=rec_help(d.CANCER_RELATED_PROCEDURE, "reason_reference"))
    extra_properties = JSONField(blank=True, null=True,
                                 help_text=rec_help(d.CANCER_RELATED_PROCEDURE, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.id)


# ==== Medication Statement ====


class MedicationStatement(models.Model, IndexableMixin):
    """
    Class to record the use of a medication.
    """

    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.MEDICATION_STATEMENT, "id"))
    # list http://hl7.org/fhir/us/core/STU3.1/ValueSet-us-core-medication-codes.html
    medication_code = JSONField(validators=[ontology_validator],
                                help_text=rec_help(d.MEDICATION_STATEMENT, "medication_code"))
    termination_reason = JSONField(null=True, validators=[ontology_list_validator],
                                   help_text=rec_help(d.MEDICATION_STATEMENT, 'termination_reason'))
    treatment_intent = JSONField(blank=True, null=True, validators=[ontology_validator],
                                 help_text=rec_help(d.MEDICATION_STATEMENT, "treatment_intent"))
    start_date = models.DateTimeField(blank=True, null=True, help_text=rec_help(d.MEDICATION_STATEMENT, "start_date"))
    end_date = models.DateTimeField(blank=True, null=True, help_text=rec_help(d.MEDICATION_STATEMENT, "end_date"))
    extra_properties = JSONField(blank=True, null=True,
                                 help_text=rec_help(d.MEDICATION_STATEMENT, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.id)


class MCodePacket(models.Model, IndexableMixin):
    """
    Class to aggregate Individual's cancer related metadata
    """

    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.MCODEPACKET, "id"))
    subject = models.ForeignKey(Individual, on_delete=models.CASCADE,
                                help_text=rec_help(d.MCODEPACKET, "subject"))
    genomics_report = models.ForeignKey(GenomicsReport, blank=True, null=True, on_delete=models.SET_NULL,
                                        help_text=rec_help(d.MCODEPACKET, "genomics_report"))
    cancer_condition = models.ManyToManyField(CancerCondition, blank=True,
                                              help_text=rec_help(d.MCODEPACKET, "cancer_condition"))
    cancer_related_procedures = models.ManyToManyField(CancerRelatedProcedure, blank=True,
                                                       help_text=rec_help(d.MCODEPACKET, "cancer_related_procedures"))
    medication_statement = models.ManyToManyField(MedicationStatement, blank=True,
                                                  help_text=rec_help(d.MCODEPACKET, "medication_statement"))
    date_of_death = models.CharField(max_length=200, blank=True, help_text=rec_help(d.MCODEPACKET, "date_of_death"))
    cancer_disease_status = JSONField(blank=True, null=True, validators=[ontology_validator],
                                      help_text=rec_help(d.MCODEPACKET, "cancer_disease_status"))
    # link to dataset via the table
    table = models.ForeignKey("chord.Table", on_delete=models.CASCADE, blank=True, null=True)  # TODO: Help text
    extra_properties = JSONField(blank=True, null=True,
                                 help_text=rec_help(d.MCODEPACKET, "extra_properties"))
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.id)
