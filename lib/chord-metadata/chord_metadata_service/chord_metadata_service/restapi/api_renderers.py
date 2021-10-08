import json
import csv
from djangorestframework_camel_case.render import CamelCaseJSONRenderer
from rest_framework.renderers import JSONRenderer
from rdflib import Graph
from rdflib.plugin import register, Serializer
from django.http import HttpResponse

from uuid import UUID

from .jsonld_utils import dataset_to_jsonld
from .utils import parse_onset

register('json-ld', Serializer, 'rdflib_jsonld.serializer', 'JsonLDSerializer')


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)


class FHIRRenderer(JSONRenderer):
    media_type = 'application/json'
    format = 'fhir'

    def render(self, data, media_type=None, renderer_context=None):
        fhir_datatype_plural = getattr(
            renderer_context.get('view').get_serializer().Meta,
            'fhir_datatype_plural', 'objects'
        )
        class_converter = getattr(
            renderer_context.get('view').get_serializer().Meta,
            'class_converter', 'objects'
        )
        if 'results' in data:
            final_data = {fhir_datatype_plural: [class_converter(item) for item in data['results']]}
        else:
            final_data = class_converter(data)
        return super(FHIRRenderer, self).render(final_data, media_type, renderer_context)


class PhenopacketsRenderer(CamelCaseJSONRenderer):
    media_type = 'application/json'
    format = 'phenopackets'

    def render(self, data, media_type=None, renderer_context=None):
        return super(PhenopacketsRenderer, self).render(data, media_type, renderer_context)


class JSONLDDatasetRenderer(PhenopacketsRenderer):
    media_type = 'application/ld+json'
    format = 'json-ld'

    def render(self, data, media_type=None, renderer_context=None):
        if 'results' in data:
            json_obj = {'results': [dataset_to_jsonld(item) for item in data['results']]}
        else:
            json_obj = dataset_to_jsonld(data)

        return super(JSONLDDatasetRenderer, self).render(json_obj, media_type, renderer_context)


class RDFDatasetRenderer(PhenopacketsRenderer):
    # change for 'application/rdf+xml'
    media_type = 'application/rdf+xml'
    render_style = 'binary'
    charset = 'utf-8'
    format = 'rdf'

    def render(self, data, media_type=None, renderer_context=None):
        if 'results' in data:
            g = Graph()
            for item in data['results']:
                ld_context_item = dataset_to_jsonld(item)
                small_g = Graph().parse(data=json.dumps(ld_context_item, cls=UUIDEncoder), format='json-ld')
                # join graphs
                g = g + small_g
        else:
            ld_context_data = dataset_to_jsonld(data)
            g = Graph().parse(data=json.dumps(ld_context_data, cls=UUIDEncoder), format='json-ld')
        rdf_data = g.serialize(format='pretty-xml')
        return rdf_data


class IndividualCSVRenderer(JSONRenderer):
    media_type = 'text/csv'
    format = 'csv'

    def render(self, data, media_type=None, renderer_context=None):
        if 'results' in data:
            individuals = []
            for individual in data['results']:
                ind_obj = {
                    'id': individual['id'],
                    'sex': individual.get('sex', None),
                    'date_of_birth': individual.get('date_of_birth', None),
                    'taxonomy': None,
                    'karyotypic_sex': individual['karyotypic_sex'],
                    'race': individual.get('race', None),
                    'ethnicity': individual.get('ethnicity', None),
                    'age': None,
                    'diseases': None,
                    'created': individual['created'],
                    'updated': individual['updated']
                }
                if 'taxonomy' in individual:
                    ind_obj['taxonomy'] = individual['taxonomy'].get('label', None)
                if 'age' in individual:
                    if 'age' in individual['age']:
                        ind_obj['age'] = individual['age'].get('age', None)
                    elif 'start' and 'end' in individual['age']:
                        ind_obj['age'] = str(
                            individual['age']['start'].get('age', "NA")
                            + ' - ' +
                            individual['age']['end'].get('age', "NA")
                        )
                    else:
                        ind_obj['age'] = None
                if 'phenopackets' in individual:
                    all_diseases = []
                    for phenopacket in individual['phenopackets']:
                        if 'diseases' in phenopacket:
                            # use ; because some disease terms might contain , in their label
                            single_phenopacket_diseases = '; '.join(
                                [
                                    f"{d['term']['label']} ({parse_onset(d['onset'])})"
                                    if 'onset' in d else d['term']['label'] for d in phenopacket['diseases']
                                ]
                            )
                            all_diseases.append(single_phenopacket_diseases)
                    if all_diseases:
                        ind_obj['diseases'] = '; '.join(all_diseases)
                individuals.append(ind_obj)
            columns = individuals[0].keys()
            # remove underscore and capitalize column names
            headers = {key: key.replace('_', ' ').capitalize() for key in individuals[0].keys()}
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = "attachment; filename='export.csv'"
            dict_writer = csv.DictWriter(response, fieldnames=columns)
            dict_writer.writerow(headers)
            dict_writer.writerows(individuals)
            return response
