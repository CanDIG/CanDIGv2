import django_filters
from django.db.models import Q

from .models import Individual


class IndividualFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.AllValuesMultipleFilter()
    sex = django_filters.CharFilter(lookup_expr='iexact')
    karyotypic_sex = django_filters.CharFilter(lookup_expr='iexact')
    ethnicity = django_filters.CharFilter(lookup_expr='icontains')
    race = django_filters.CharFilter(lookup_expr='icontains')
    # e.g. date_of_birth_after=1987-01-01&date_of_birth_before=1990-12-31
    date_of_birth = django_filters.DateFromToRangeFilter()
    disease = django_filters.CharFilter(
        method="filter_disease", field_name="phenopackets__diseases",
        label="Disease"
    )
    # e.g. select all patients who have a symptom "dry cough"
    found_phenotypic_feature = django_filters.CharFilter(
        method="filter_found_phenotypic_feature", field_name="phenopackets__phenotypic_features",
        label="Found phenotypic feature"
    )

    class Meta:
        model = Individual
        fields = ["id", "active", "deceased", "phenopackets__biosamples", "phenopackets"]

    def filter_found_phenotypic_feature(self, qs, name, value):
        """
        Filters only found (present in a patient) Phenotypic features by id or label
        """
        qs = qs.filter(
            Q(phenopackets__phenotypic_features__pftype__id__icontains=value) |
            Q(phenopackets__phenotypic_features__pftype__label__icontains=value),
            phenopackets__phenotypic_features__negated=False
        ).distinct()
        return qs

    def filter_disease(self, qs, name, value):
        qs = qs.filter(
            Q(phenopackets__diseases__term__id__icontains=value) |
            Q(phenopackets__diseases__term__label__icontains=value)
        ).distinct()
        return qs
