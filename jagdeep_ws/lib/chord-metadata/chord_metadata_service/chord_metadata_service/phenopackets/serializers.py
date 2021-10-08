import re
from rest_framework import serializers
from .models import (
    MetaData,
    PhenotypicFeature,
    Procedure,
    HtsFile,
    Gene,
    Variant,
    Disease,
    Biosample,
    Phenopacket,
    GenomicInterpretation,
    Diagnosis,
    Interpretation,
)
from chord_metadata_service.resources.serializers import ResourceSerializer
from chord_metadata_service.restapi import fhir_utils
from chord_metadata_service.restapi.serializers import GenericSerializer


__all__ = [
    "MetaDataSerializer",
    "PhenotypicFeatureSerializer",
    "ProcedureSerializer",
    "HtsFileSerializer",
    "GeneSerializer",
    "VariantSerializer",
    "DiseaseSerializer",
    "BiosampleSerializer",
    "SimplePhenopacketSerializer",
    "PhenopacketSerializer",
    "GenomicInterpretationSerializer",
    "DiagnosisSerializer",
    "InterpretationSerializer",
]


#############################################################
#                                                           #
#                  Metadata  Serializers                    #
#                                                           #
#############################################################


class MetaDataSerializer(GenericSerializer):
    resources = ResourceSerializer(read_only=True, many=True)

    class Meta:
        model = MetaData
        fields = '__all__'


#############################################################
#                                                           #
#              Phenotypic Data  Serializers                 #
#                                                           #
#############################################################

class PhenotypicFeatureSerializer(GenericSerializer):
    always_include = (
        "negated",
    )

    type = serializers.JSONField(source='pftype')

    class Meta:
        model = PhenotypicFeature
        exclude = ['pftype']
        # meta info for converting to FHIR
        fhir_datatype_plural = 'observations'
        class_converter = fhir_utils.fhir_observation


class ProcedureSerializer(GenericSerializer):

    class Meta:
        model = Procedure
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'specimen.collections'
        class_converter = fhir_utils.fhir_specimen_collection

    def create(self, validated_data):
        if validated_data.get('body_site'):
            instance, _ = Procedure.objects.get_or_create(**validated_data)
        else:
            instance, _ = Procedure.objects.get_or_create(
                code=validated_data.get('code'), body_site__isnull=True)
        return instance


class HtsFileSerializer(GenericSerializer):

    class Meta:
        model = HtsFile
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'document_references'
        class_converter = fhir_utils.fhir_document_reference


class GeneSerializer(GenericSerializer):
    alternate_ids = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        allow_empty=True, required=False)

    class Meta:
        model = Gene
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'observations'
        class_converter = fhir_utils.fhir_obs_component_region_studied


class VariantSerializer(GenericSerializer):

    class Meta:
        model = Variant
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'observations'
        class_converter = fhir_utils.fhir_obs_component_variant

    def to_representation(self, obj):
        """ Change 'allele_type' field name to allele type value. """

        output = super().to_representation(obj)
        output[obj.allele_type] = output.pop('allele')
        return output

    def to_internal_value(self, data):
        """ When writing back to db change field name back to 'allele'. """

        if 'allele' not in data.keys():
            allele_type = data.get('allele_type')  # e.g. spdiAllele
            # split by uppercase
            normilize = filter(None, re.split("([A-Z][^A-Z]*)", allele_type))
            normilized_allele_type = '_'.join([i.lower() for i in normilize])
            data['allele'] = data.pop(normilized_allele_type)
        return super(VariantSerializer, self).to_internal_value(data=data)


class DiseaseSerializer(GenericSerializer):

    class Meta:
        model = Disease
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'conditions'
        class_converter = fhir_utils.fhir_condition


class BiosampleSerializer(GenericSerializer):
    phenotypic_features = PhenotypicFeatureSerializer(
        read_only=True, many=True, exclude_when_nested=['id', 'biosample'])
    procedure = ProcedureSerializer(exclude_when_nested=['id'])
    variants = VariantSerializer(read_only=True, many=True)

    class Meta:
        model = Biosample
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'specimens'
        class_converter = fhir_utils.fhir_specimen

    def create(self, validated_data):
        procedure_data = validated_data.pop('procedure')
        procedure_model, _ = Procedure.objects.get_or_create(**procedure_data)
        biosample = Biosample.objects.create(procedure=procedure_model, **validated_data)
        return biosample

    def update(self, instance, validated_data):
        instance.sampled_tissue = validated_data.get('sampled_tissue', instance.sampled_tissue)
        instance.individual_age_at_collection = validated_data.get('individual_age_at_collection',
                                                                   instance.individual_age_at_collection)
        instance.taxonomy = validated_data.get('taxonomy', instance.taxonomy)
        instance.histological_diagnosis = validated_data.get('histological_diagnosis', instance.histological_diagnosis)
        instance.tumor_progression = validated_data.get('tumor_progression', instance.tumor_progression)
        instance.tumor_grade = validated_data.get('tumor_grade', instance.tumor_grade)
        instance.diagnostic_markers = validated_data.get('diagnostic_markers', instance.diagnostic_markers)
        instance.save()
        procedure_data = validated_data.pop('procedure', None)
        if procedure_data:
            instance.procedure, _ = Procedure.objects.get_or_create(**procedure_data)
        instance.save()
        return instance


class SimplePhenopacketSerializer(GenericSerializer):
    phenotypic_features = PhenotypicFeatureSerializer(
        read_only=True, many=True, exclude_when_nested=['id', 'biosample'])

    class Meta:
        model = Phenopacket
        fields = '__all__'
        # meta info for converting to FHIR
        fhir_datatype_plural = 'compositions'
        class_converter = fhir_utils.fhir_composition

    def to_representation(self, instance):
        """"
        Overriding this method to allow post Primary Key for FK and M2M
        objects and return their nested serialization.

        """
        response = super().to_representation(instance)
        response['biosamples'] = BiosampleSerializer(instance.biosamples, many=True, required=False,
                                                     exclude_when_nested=["individual"]).data
        response['genes'] = GeneSerializer(instance.genes, many=True, required=False).data
        response['variants'] = VariantSerializer(instance.variants, many=True, required=False).data
        response['diseases'] = DiseaseSerializer(instance.diseases, many=True, required=False).data
        response['hts_files'] = HtsFileSerializer(instance.hts_files, many=True, required=False).data
        response['meta_data'] = MetaDataSerializer(instance.meta_data, exclude_when_nested=['id']).data
        return response


class PhenopacketSerializer(SimplePhenopacketSerializer):

    def to_representation(self, instance):
        # Phenopacket serializer for nested individuals - need to import here to
        # prevent circular import issues.
        from chord_metadata_service.patients.serializers import IndividualSerializer
        response = super().to_representation(instance)
        response['subject'] = IndividualSerializer(
            instance.subject,
            exclude_when_nested=["phenopackets", "biosamples"]
            ).data
        return response


#############################################################
#                                                           #
#                Interpretation Serializers                 #
#                                                           #
#############################################################

class GenomicInterpretationSerializer(GenericSerializer):
    class Meta:
        model = GenomicInterpretation
        fields = '__all__'


class DiagnosisSerializer(GenericSerializer):
    class Meta:
        model = Diagnosis
        fields = '__all__'


class InterpretationSerializer(GenericSerializer):
    class Meta:
        model = Interpretation
        fields = '__all__'
