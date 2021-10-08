from django.urls import path, include
from rest_framework import routers

from chord_metadata_service.chord import api_views as chord_views
from chord_metadata_service.experiments import api_views as experiment_views
from chord_metadata_service.mcode import api_views as mcode_views
from chord_metadata_service.patients import api_views as individual_views
from chord_metadata_service.phenopackets import api_views as phenopacket_views
from chord_metadata_service.resources import api_views as resources_views

__all__ = ["router", "urlpatterns"]

router = routers.DefaultRouter(trailing_slash=False)

# CHORD app urls
router.register(r'projects', chord_views.ProjectViewSet)
router.register(r'datasets', chord_views.DatasetViewSet)
router.register(r'table_ownership', chord_views.TableOwnershipViewSet)
router.register(r'tables', chord_views.TableViewSet)

# Experiments app urls
router.register(r'experiments', experiment_views.ExperimentViewSet)

# Patients app urls
router.register(r'individuals', individual_views.IndividualViewSet)

# Phenopackets app urls
router.register(r'phenotypicfeatures', phenopacket_views.PhenotypicFeatureViewSet)
router.register(r'procedures', phenopacket_views.ProcedureViewSet)
router.register(r'htsfiles', phenopacket_views.HtsFileViewSet)
router.register(r'genes', phenopacket_views.GeneViewSet)
router.register(r'variants', phenopacket_views.VariantViewSet)
router.register(r'diseases', phenopacket_views.DiseaseViewSet)
router.register(r'metadata', phenopacket_views.MetaDataViewSet)
router.register(r'biosamples', phenopacket_views.BiosampleViewSet)
router.register(r'phenopackets', phenopacket_views.PhenopacketViewSet)
router.register(r'genomicinterpretations', phenopacket_views.GenomicInterpretationViewSet)
router.register(r'diagnoses', phenopacket_views.DiagnosisViewSet)
router.register(r'interpretations', phenopacket_views.InterpretationViewSet)

# mCode app urls
router.register(r'geneticspecimens', mcode_views.GeneticSpecimenViewSet)
router.register(r'cancergeneticvariants', mcode_views.CancerGeneticVariantViewSet)
router.register(r'genomicregionsstudied', mcode_views.GenomicRegionStudiedViewSet)
router.register(r'genomicsreports', mcode_views.GenomicsReportViewSet)
router.register(r'labsvital', mcode_views.LabsVitalViewSet)
router.register(r'cancerconditions', mcode_views.CancerConditionViewSet)
router.register(r'tnmstaging', mcode_views.TNMStagingViewSet)
router.register(r'cancerrelatedprocedures', mcode_views.CancerRelatedProcedureViewSet)
router.register(r'medicationstatements', mcode_views.MedicationStatementViewSet)
router.register(r'mcodepackets', mcode_views.MCodePacketViewSet)

# Resources app urls
router.register(r'resources', resources_views.ResourceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # apps schemas
    path('chord_phenopacket_schema', phenopacket_views.get_chord_phenopacket_schema,
         name="chord-phenopacket-schema"),
    path('experiment_schema', experiment_views.get_experiment_schema,
         name="experiment-schema"),
    path('mcode_schema', mcode_views.get_mcode_schema,
         name="mcode-schema"),
    # overview
    path('overview', phenopacket_views.phenopackets_overview,
         name="overview"),
]
