from chord_metadata_service.restapi.serializers import GenericSerializer
from chord_metadata_service.patients.serializers import IndividualSerializer
from . import models as m


__all__ = [
    "GeneticSpecimenSerializer",
    "CancerGeneticVariantSerializer",
    "GenomicRegionStudiedSerializer",
    "GenomicsReportSerializer",
    "LabsVitalSerializer",
    "TNMStagingSerializer",
    "CancerConditionSerializer",
    "CancerRelatedProcedureSerializer",
    "MedicationStatementSerializer",
    "MCodePacketSerializer",
]


class GeneticSpecimenSerializer(GenericSerializer):

    class Meta:
        model = m.GeneticSpecimen
        fields = '__all__'


class CancerGeneticVariantSerializer(GenericSerializer):

    class Meta:
        model = m.CancerGeneticVariant
        fields = '__all__'


class GenomicRegionStudiedSerializer(GenericSerializer):

    class Meta:
        model = m.GenomicRegionStudied
        fields = '__all__'


class GenomicsReportSerializer(GenericSerializer):

    class Meta:
        model = m.GenomicsReport
        fields = '__all__'

    def to_representation(self, instance):
        """"
        Overriding this method to allow post Primary Key for FK and M2M
        objects and return their nested serialization.
        """
        response = super().to_representation(instance)
        return response


class LabsVitalSerializer(GenericSerializer):

    class Meta:
        model = m.LabsVital
        fields = '__all__'


class TNMStagingSerializer(GenericSerializer):

    class Meta:
        model = m.TNMStaging
        fields = '__all__'


class CancerConditionSerializer(GenericSerializer):
    tnm_staging = TNMStagingSerializer(source='tnmstaging_set', read_only=True, many=True)

    class Meta:
        model = m.CancerCondition
        fields = '__all__'


class CancerRelatedProcedureSerializer(GenericSerializer):

    class Meta:
        model = m.CancerRelatedProcedure
        fields = '__all__'


class MedicationStatementSerializer(GenericSerializer):

    class Meta:
        model = m.MedicationStatement
        fields = '__all__'


class MCodePacketSerializer(GenericSerializer):

    def to_representation(self, instance):
        """"
        Overriding this method to allow post Primary Key for FK and M2M
        objects and return their nested serialization.
        """
        response = super().to_representation(instance)
        response['subject'] = IndividualSerializer(instance.subject).data
        response['genomics_report'] = GenomicsReportSerializer(instance.genomics_report, required=False).data
        response['cancer_condition'] = CancerConditionSerializer(instance.cancer_condition, many=True,
                                                                 required=False).data
        response['cancer_related_procedures'] = CancerRelatedProcedureSerializer(instance.cancer_related_procedures,
                                                                                 many=True, required=False).data
        response['medication_statement'] = MedicationStatementSerializer(instance.medication_statement,
                                                                         many=True, required=False).data
        # TODO add tumor marker
        return response

    class Meta:
        model = m.MCodePacket
        fields = '__all__'
