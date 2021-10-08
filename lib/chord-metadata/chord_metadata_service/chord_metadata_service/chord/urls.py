from django.urls import path

from . import views_ingest, views_search

urlpatterns = [
    path('workflows', views_ingest.workflow_list, name="workflows"),
    path('workflows/<slug:workflow_id>', views_ingest.workflow_item, name="workflow-detail"),
    path('workflows/<slug:workflow_id>.wdl', views_ingest.workflow_file, name="workflow-file"),

    path('private/ingest', views_ingest.ingest, name="ingest"),

    path('data-types', views_search.data_type_list, name="data-type-list"),
    path('data-types/<str:data_type>', views_search.data_type_detail, name="data-type-detail"),
    path('data-types/<str:data_type>/schema', views_search.data_type_schema, name="data-type-schema"),
    # TODO: Consistent snake or kebab
    path('data-types/<str:data_type>/metadata_schema', views_search.data_type_metadata_schema,
         name="data-type-metadata-schema"),
    path('tables', views_search.table_list, name="chord-table-list"),
    path('tables/<str:table_id>', views_search.table_detail, name="chord-table-detail"),
    path('tables/<str:table_id>/summary', views_search.chord_table_summary, name="table-summary"),
    path('tables/<str:table_id>/search', views_search.chord_public_table_search, name="public-table-search"),
    path('search', views_search.chord_search, name="search"),
    path('fhir-search', views_search.fhir_public_search, name="fhir-search"),
    path('private/fhir-search', views_search.fhir_private_search, name="fhir-private-search"),
    path('private/search', views_search.chord_private_search, name="private-search"),
    path('private/tables/<str:table_id>/search', views_search.chord_private_table_search, name="private-table-search"),
]
