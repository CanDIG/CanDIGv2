from django.contrib import admin
from . import models as m


@admin.register(m.GeneticSpecimen)
class GeneticSpecimenAdmin(admin.ModelAdmin):
    pass


@admin.register(m.CancerGeneticVariant)
class CancerGeneticVariantAdmin(admin.ModelAdmin):
    pass


@admin.register(m.GenomicRegionStudied)
class GenomicRegionStudiedAdmin(admin.ModelAdmin):
    pass


@admin.register(m.GenomicsReport)
class GenomicsReportAdmin(admin.ModelAdmin):
    pass


@admin.register(m.LabsVital)
class LabsVitalAdmin(admin.ModelAdmin):
    pass


@admin.register(m.CancerCondition)
class CancerConditionAdmin(admin.ModelAdmin):
    pass


@admin.register(m.TNMStaging)
class TNMStagingAdmin(admin.ModelAdmin):
    pass


@admin.register(m.CancerRelatedProcedure)
class CancerRelatedProcedureAdmin(admin.ModelAdmin):
    pass


@admin.register(m.MedicationStatement)
class MedicationStatementAdmin(admin.ModelAdmin):
    pass


@admin.register(m.MCodePacket)
class MCodePacketAdmin(admin.ModelAdmin):
    pass
