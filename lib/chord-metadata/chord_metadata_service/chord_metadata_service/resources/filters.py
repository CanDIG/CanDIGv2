import django_filters
from .models import Resource


class ResourceFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    namespace_prefix = django_filters.CharFilter(lookup_expr='iexact')
    url = django_filters.CharFilter(lookup_expr='iexact')
    iri_prefix = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Resource
        fields = ["id", "name",
                  "namespace_prefix", "url",
                  "version", "iri_prefix"]
