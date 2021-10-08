from django.contrib import admin
from .models import Individual

# TODO: This should not be available outside of development mode.


@admin.register(Individual)
class IndividualAdmin(admin.ModelAdmin):
    pass
