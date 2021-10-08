from datetime import datetime
from fhirclient.models import (
    observation as obs,
    patient as p,
    extension,
    age,
    coding as c,
    codeableconcept,
    specimen as s,
    identifier as fhir_indentifier,
    annotation as a,
    range as range_,
    quantity,
    fhirreference,
    documentreference,
    attachment,
    fhirdate,
    condition as cond,
    composition as comp,
)

from chord_metadata_service.restapi.semantic_mappings.phenopackets_on_fhir_mapping import PHENOPACKETS_ON_FHIR_MAPPING
from chord_metadata_service.restapi.semantic_mappings.hl7_genomics_mapping import HL7_GENOMICS_MAPPING


# ===================== Generic FHIR conversion functions =====================


def fhir_coding_util(obj):
    """ Generic function to convert object to FHIR Coding. """

    coding = c.Coding()
    coding.display = obj['label']
    coding.code = obj['id']
    if 'system' in obj.keys():
        coding.system = obj['system']
    return coding


def fhir_codeable_concept(obj):
    """ Generic function to convert object to FHIR CodeableConcept. """

    codeable_concept = codeableconcept.CodeableConcept()
    codeable_concept.coding = []
    if isinstance(obj, list):
        for item in obj:
            coding = fhir_coding_util(item)
            codeable_concept.coding.append(coding)
    else:
        coding = fhir_coding_util(obj)
        codeable_concept.coding.append(coding)
    return codeable_concept


def codeable_concepts_fields(field_list, profile, obj):
    """ Converts a list of fields to FHIR CodeableConcepts and returns a list of extensions. """
    concept_extensions = []
    for field in field_list:
        if field in obj.keys():
            codeable_concepts_extension = extension.Extension()
            codeable_concepts_extension.url = PHENOPACKETS_ON_FHIR_MAPPING[profile][field]
            codeable_concepts_extension.valueCodeableConcept = fhir_codeable_concept(obj[field])
            concept_extensions.append(codeable_concepts_extension)
    return concept_extensions


def fhir_age(obj, mapping, field):
    """ Generic function to convert Age or AgeRange to FHIR Age. """

    age_extension = extension.Extension()
    age_extension.url = mapping

    if "start" in obj[field]:  # Is an age range
        age_extension.valueRange = range_.Range()
        age_extension.valueRange.low = quantity.Quantity()
        age_extension.valueRange.low.unit = obj[field]['start']['age']
        age_extension.valueRange.high = quantity.Quantity()
        age_extension.valueRange.high.unit = obj[field]['end']['age']
    else:  # Is a precise age
        age_extension.valueAge = age.Age()
        age_extension.valueAge.unit = obj[field]['age']
    return age_extension


def check_disease_onset(disease):
    """
    Phenopackets schema allows age to be represented by ISO8601 string,
    whereis Pheno-FHIR guide requires it to be represented by CodeableConcept.
    This function checks how age is represented in data.
    """
    if disease.get('onset'):
        if isinstance(disease.get('onset').get('age'), dict):
            if disease.get('onset').get('age').get('label') is not None:
                return True
    return False


# ============== Phenopackets to FHIR class conversion functions ==============


def fhir_patient(obj):
    """ Converts Individual to FHIR Patient. """

    patient = p.Patient()
    patient.id = obj['id']
    patient.birthDate = fhirdate.FHIRDate(obj.get('date_of_birth', None))
    patient.gender = obj.get('sex', None)
    patient.active = obj.get('active', None)
    patient.deceasedBoolean = obj.get('deceased', None)
    patient.extension = list()
    # age
    if 'age' in obj.keys():
        age_extension = fhir_age(obj, PHENOPACKETS_ON_FHIR_MAPPING['individual']['age'], 'age')
        patient.extension.append(age_extension)
    # karyotypic_sex
    karyotypic_sex_extension = extension.Extension()
    karyotypic_sex_extension.url = PHENOPACKETS_ON_FHIR_MAPPING['individual']['karyotypic_sex']['url']
    karyotypic_sex_extension.valueCodeableConcept = codeableconcept.CodeableConcept()
    karyotypic_sex_extension.valueCodeableConcept.coding = list()
    coding = c.Coding()
    coding.display = obj.get('karyotypic_sex', None)
    coding.code = obj.get('karyotypic_sex', None)
    coding.system = PHENOPACKETS_ON_FHIR_MAPPING['individual']['karyotypic_sex']['system']
    karyotypic_sex_extension.valueCodeableConcept.coding.append(coding)
    patient.extension.append(karyotypic_sex_extension)
    # taxonomy
    if 'taxonomy' in obj.keys():
        taxonomy_extension = extension.Extension()
        taxonomy_extension.url = PHENOPACKETS_ON_FHIR_MAPPING['individual']['taxonomy']
        taxonomy_extension.valueCodeableConcept = codeableconcept.CodeableConcept()
        taxonomy_extension.valueCodeableConcept.coding = list()
        coding = c.Coding()
        coding.display = obj.get('taxonomy', None).get('label', None)
        coding.code = obj.get('taxonomy', None).get('id', None)
        taxonomy_extension.valueCodeableConcept.coding.append(coding)
        patient.extension.append(taxonomy_extension)
    return patient.as_json()


def fhir_specimen_collection(obj):
    """ Converts Procedure to FHIR Specimen collection. """

    collection = s.SpecimenCollection()
    collection.id = str(obj['id'])
    collection.method = fhir_codeable_concept(obj['code'])
    if 'body_site' in obj.keys():
        collection.bodySite = fhir_codeable_concept(obj['body_site'])
    return collection.as_json()


def fhir_observation(obj):
    """ Converts phenotypic feature to FHIR Observation. """

    observation = obs.Observation()
    if 'description' in obj.keys():
        observation.note = []
        annotation = a.Annotation()
        annotation.text = obj.get('description')
        observation.note.append(annotation)
    observation.code = fhir_codeable_concept(obj['type'])
    # required by FHIR specs but omitted by phenopackets, for now set for unknown
    observation.status = 'unknown'
    if 'negated' in obj.keys():
        observation.interpretation = fhir_codeable_concept(
            {"label": "Positive", "id": "POS"}
        )
    else:
        observation.interpretation = fhir_codeable_concept(
            {"label": "Negative", "id": "NEG"}
        )
    observation.extension = []
    concept_extensions = codeable_concepts_fields(
        ['severity', 'modifier', 'onset'], 'phenotypic_feature', obj
    )
    for ce in concept_extensions:
        observation.extension.append(ce)
    if 'evidence' in obj.keys():
        evidence = extension.Extension()
        evidence.url = PHENOPACKETS_ON_FHIR_MAPPING['phenotypic_feature']['evidence']['url']
        evidence.extension = []
        evidence_code = extension.Extension()
        evidence_code.url = PHENOPACKETS_ON_FHIR_MAPPING['phenotypic_feature']['evidence']['evidence_code']
        evidence_code.valueCodeableConcept = fhir_codeable_concept(obj['evidence']['evidence_code'])
        evidence.extension.append(evidence_code)
        if 'reference' in obj['evidence'].keys():
            evidence_reference = extension.Extension()
            evidence_reference.url = PHENOPACKETS_ON_FHIR_MAPPING['external_reference']['url']
            evidence_reference.extension = []
            evidence_reference_id = extension.Extension()
            evidence_reference_id.url = PHENOPACKETS_ON_FHIR_MAPPING['external_reference']['id_url']
            # GA$GH guide requires valueURL but there is no such property
            evidence_reference_id.valueUri = obj['evidence']['reference']['id']
            evidence_reference.extension.append(evidence_reference_id)
            if 'description' in obj['evidence']['reference'].keys():
                evidence_reference_desc = extension.Extension()
                evidence_reference_desc.url = PHENOPACKETS_ON_FHIR_MAPPING['external_reference']['description_url']
                evidence_reference_desc.valueString = obj['evidence']['reference'].get('description', None)
                evidence_reference.extension.append(evidence_reference_desc)
            evidence.extension.append(evidence_reference)
        observation.extension.append(evidence)

    if 'biosample' in obj.keys():
        observation.specimen = fhirreference.FHIRReference()
        observation.specimen.reference = obj.get('biosample', None)
    return observation.as_json()


def fhir_specimen(obj):
    """ Converts biosample to FHIR Specimen. """

    specimen = s.Specimen()
    specimen.identifier = []
    # id
    identifier = fhir_indentifier.Identifier()
    identifier.value = obj['id']
    specimen.identifier.append(identifier)
    # individual - subject property in FHIR is mandatory for a specimen
    specimen.subject = fhirreference.FHIRReference()
    specimen.subject.reference = obj.get('individual', 'unknown')
    # sampled_tissue
    specimen.type = codeableconcept.CodeableConcept()
    specimen.type.coding = []
    coding = c.Coding()
    coding.code = obj['sampled_tissue']['id']
    coding.display = obj['sampled_tissue']['label']
    specimen.type.coding.append(coding)
    # description
    if 'description' in obj.keys():
        specimen.note = []
        annotation = a.Annotation()
        annotation.text = obj.get('description', None)
        specimen.note.append(annotation)
    # procedure
    specimen.collection = s.SpecimenCollection()
    specimen.collection.method = fhir_codeable_concept(obj['procedure']['code'])
    if 'body_site' in obj['procedure'].keys():
        specimen.collection.bodySite = fhir_codeable_concept(obj['procedure']['body_site'])
    # Note on taxonomy from phenopackets specs:
    # Individuals already contain a taxonomy attribute so this attribute is not needed.
    # extensions
    specimen.extension = []
    # individual_age_at_collection
    if 'individual_age_at_collection' in obj.keys():
        ind_age_at_collection_extension = fhir_age(
            obj, PHENOPACKETS_ON_FHIR_MAPPING['biosample']['individual_age_at_collection'],
            'individual_age_at_collection'
        )
        specimen.extension.append(ind_age_at_collection_extension)
    concept_extensions = codeable_concepts_fields(
        ['histological_diagnosis', 'tumor_progression', 'tumor_grade', 'diagnostic_markers'],
        'biosample', obj
    )
    for concept in concept_extensions:
        specimen.extension.append(concept)

    if 'is_control_sample' in obj.keys():
        control_extension = extension.Extension()
        control_extension.url = PHENOPACKETS_ON_FHIR_MAPPING['biosample']['is_control_sample']
        control_extension.valueBoolean = obj['is_control_sample']
        specimen.extension.append(control_extension)
    # TODO 2m extensions - references
    return specimen.as_json()


def fhir_document_reference(obj):
    """ Converts HTS file to FHIR DocumentReference. """

    doc_ref = documentreference.DocumentReference()
    doc_ref.type = fhir_codeable_concept({"label": obj['hts_format'], "id": obj['hts_format']})
    # GA4GH requires status with the fixed value
    doc_ref.status = PHENOPACKETS_ON_FHIR_MAPPING['hts_file']['status']
    doc_ref.content = []
    doc_content = documentreference.DocumentReferenceContent()
    doc_content.attachment = attachment.Attachment()
    doc_content.attachment.url = obj['uri']
    if 'description' in obj.keys():
        doc_content.attachment.title = obj.get('description', None)
    doc_ref.content.append(doc_content)
    doc_ref.indexed = fhirdate.FHIRDate()
    # check what date it should be  - when it's retrieved or created
    doc_ref.indexed.date = datetime.now()
    doc_ref.extension = []
    genome_assembly = extension.Extension()
    genome_assembly.url = PHENOPACKETS_ON_FHIR_MAPPING['hts_file']['genome_assembly']
    genome_assembly.valueString = obj['genome_assembly']
    doc_ref.extension.append(genome_assembly)
    return doc_ref.as_json()


def fhir_obs_component_region_studied(obj):
    """ Gene corresponds to Observation.component."""

    # GA4GH to FHIR Mapping Guide provides a link to
    # Genomics Reporting Implementation Guide (STU1) mapping
    # http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/region-studied

    component = obs.ObservationComponent()
    component.code = fhir_codeable_concept(HL7_GENOMICS_MAPPING['gene']['gene_studied_code'])
    component.valueCodeableConcept = fhir_codeable_concept({
        "id": obj['id'],
        "label": obj['symbol'],
        "system": HL7_GENOMICS_MAPPING['gene']['gene_studied_value']['system']
    })
    return component.as_json()


def fhir_obs_component_variant(obj):
    """ Variant corresponds to Observation.component:variant. """

    component = obs.ObservationComponent()
    component.code = fhir_codeable_concept(HL7_GENOMICS_MAPPING['variant']['variant_length_code'])
    component.valueCodeableConcept = fhir_codeable_concept(
        {"id": obj.get('allele_type'), "label": obj.get('allele_type')}
    )
    return component.as_json()


def fhir_condition(obj):
    """ Converts Disease to FHIR Condition. """

    condition = cond.Condition()
    condition.id = str(obj['id'])
    condition.code = fhir_codeable_concept(obj['term'])
    # subject is required by Pheno-FHIR mapping Guide and by FHIR, set to 'unknown'
    condition.subject = fhirreference.FHIRReference()
    condition.subject.reference = 'unknown'
    condition.extension = []
    # only adds disease-onset if it's ontology term
    # NOTE it is required element by Pheno-FHIR mapping guide but not Phenopackets
    if check_disease_onset(obj):
        onset_extension = extension.Extension()
        onset_extension.url = PHENOPACKETS_ON_FHIR_MAPPING['disease']['onset']
        onset_extension.valueCodeableConcept = fhir_codeable_concept(obj['onset']['age'])
        condition.extension.append(onset_extension)

    if 'disease_stage' in obj.keys():
        for item in obj['disease_stage']:
            disease_stage_extension = extension.Extension()
            disease_stage_extension.url = PHENOPACKETS_ON_FHIR_MAPPING['disease']['disease_stage']
            disease_stage_extension.valueCodeableConcept = fhir_codeable_concept(item)
            condition.extension.append(disease_stage_extension)

    return condition.as_json()


def _get_section_object(nested_obj, title):
    """ Internal function to convert phenopacket m2m objects to Composition section. """

    section_content = comp.CompositionSection()
    section_values = PHENOPACKETS_ON_FHIR_MAPPING['phenopacket'][title]
    section_content.title = section_values['title']
    section_content.code = codeableconcept.CodeableConcept()
    section_content.code.coding = []
    coding = c.Coding()
    coding.system = section_values['code']['system']
    coding.version = section_values['code']['version']
    coding.code = section_values['code']['code']
    coding.display = section_values['code']['display']
    section_content.code.coding.append(coding)

    section_content.entry = []
    for item in nested_obj:
        entry = fhirreference.FHIRReference()
        if item.get('id'):
            entry.reference = str(item['id'])
        else:
            entry.reference = item['uri']
        section_content.entry.append(entry)
    return section_content


def fhir_composition(obj):
    """ Converts Phenopacket to FHIR Composition. """

    composition = comp.Composition()
    composition.id = obj['id']
    composition.subject = fhirreference.FHIRReference()
    composition.subject.reference = str(obj['subject']['id'])
    composition.title = PHENOPACKETS_ON_FHIR_MAPPING['phenopacket']['title']
    # elements in Composition required by FHIR spec
    composition.status = 'preliminary'
    composition.author = []
    author = fhirreference.FHIRReference()
    author.reference = obj['meta_data']['created_by']
    composition.author.append(author)
    composition.date = fhirdate.FHIRDate(obj['meta_data']['created'])
    composition.type = fhir_codeable_concept({
        "id": PHENOPACKETS_ON_FHIR_MAPPING['phenopacket']['code']['code'],
        "label": PHENOPACKETS_ON_FHIR_MAPPING['phenopacket']['title'],
        "system": PHENOPACKETS_ON_FHIR_MAPPING['phenopacket']['code']['system']
    })

    composition.section = []
    sections = ['biosamples', 'variants', 'diseases', 'hts_files']
    for section in sections:
        if obj[section]:
            section_content = _get_section_object(obj.get(section, None), section)
            composition.section.append(section_content)

    return composition.as_json()


# ============== FHIR to Phenopackets class conversion functions ==============
# There is no guide to map FHIR to Phenopackets

# SNOMED term to use as placeholder when collection method is not present in Specimen
procedure_not_assigned = {
    "code": {
        "id": "SNOMED:42630001",
        "label": "Procedure code not assigned",
    }
}


def patient_to_individual(obj):
    """ FHIR Patient to Individual. """

    patient = p.Patient(obj)
    individual = {
        "id": patient.id
    }
    if patient.identifier:
        individual["alternate_ids"] = [alternate_id.value for alternate_id in patient.identifier]
    gender_to_sex = {
        "male": "MALE",
        "female": "FEMALE",
        "other": "OTHER_SEX",
        "unknown": "UNKNOWN_SEX"
    }
    if patient.gender:
        individual["sex"] = gender_to_sex[patient.gender]
    if patient.birthDate:
        individual["date_of_birth"] = patient.birthDate.isostring
    if patient.active:
        individual["active"] = patient.active
    if patient.deceasedBoolean:
        individual["deceased"] = patient.deceasedBoolean
    individual["extra_properties"] = patient.as_json()
    return individual


def observation_to_phenotypic_feature(obj):
    """ FHIR Observation to Phenopackets PhenotypicFeature. """

    observation = obs.Observation(obj)
    codeable_concept = observation.code  # CodeableConcept
    phenotypic_feature = {
        # id is an integer AutoField, store legacy id in description
        # TODO change
        "description": observation.id,
        "pftype": {
            "id": f"{codeable_concept.coding[0].system}:{codeable_concept.coding[0].code}",
            "label": codeable_concept.coding[0].display
            # TODO collect system info in metadata
        }
    }
    if observation.specimen:  # FK to Biosample
        phenotypic_feature["biosample"] = observation.specimen.reference
    phenotypic_feature["extra_properties"] = observation.as_json()
    return phenotypic_feature


def condition_to_disease(obj):
    """ FHIR Condition to Phenopackets Disease. """

    condition = cond.Condition(obj)
    codeable_concept = condition.code  # CodeableConcept
    disease = {
        "term": {
            # id is an integer AutoField, legacy id can be a string
            # "id": condition.id,
            "id": f"{codeable_concept.coding[0].system}:{codeable_concept.coding[0].code}",
            "label": codeable_concept.coding[0].display
            # TODO collect system info in metadata
        },
        "extra_properties": condition.as_json()
    }
    # condition.stage.type is only in FHIR 4.0.0 version
    return disease


def specimen_to_biosample(obj):
    """ FHIR Specimen to Phenopackets Biosample. """

    specimen = s.Specimen(obj)
    biosample = {
        "id": specimen.id
    }
    if specimen.subject:
        biosample["individual"] = specimen.subject.reference
    if specimen.type:
        codeable_concept = specimen.type  # CodeableConcept
        biosample["sampled_tissue"] = {
            "id": f"{codeable_concept.coding[0].system}:{codeable_concept.coding[0].code}",
            "label": codeable_concept.coding[0].display
            # TODO collect system info in metadata
        }
    if specimen.collection:
        method_codeable_concept = specimen.collection.method
        bodysite_codeable_concept = specimen.collection.bodySite
        biosample["procedure"] = {
            "code": {
                "id": f"{method_codeable_concept.coding[0].system}:{method_codeable_concept.coding[0].code}",
                "label": method_codeable_concept.coding[0].display
            },
            "body_site": {
                "id": f"{bodysite_codeable_concept.coding[0].system}:{bodysite_codeable_concept.coding[0].code}",
                "label": bodysite_codeable_concept.coding[0].display
            }
        }
    else:
        biosample["procedure"] = procedure_not_assigned
    biosample["extra_properties"] = specimen.as_json()
    return biosample
