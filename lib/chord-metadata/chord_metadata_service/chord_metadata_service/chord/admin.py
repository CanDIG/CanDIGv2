from django.contrib import admin

from .models import Project, Dataset, TableOwnership, Table


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    pass


@admin.register(TableOwnership)
class TableOwnershipAdmin(admin.ModelAdmin):
    pass


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    pass
