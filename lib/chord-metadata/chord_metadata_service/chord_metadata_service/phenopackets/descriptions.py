# Portions of this text copyright (c) 2019-2020 the Canadian Centre for Computational Genomics; licensed under the
# GNU Lesser General Public License version 3.

# Portions of this text (c) 2019 Julius OB Jacobsen, Peter N Robinson, Christopher J Mungall; taken from the
# Phenopackets documentation: https://phenopackets-schema.readthedocs.io
# Licensed under the BSD 3-Clause License:
#   BSD 3-Clause License
#
#   Portions Copyright (c) 2018, PhenoPackets
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   * Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#   CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from chord_metadata_service.patients.descriptions import INDIVIDUAL
from chord_metadata_service.resources.descriptions import RESOURCE
from chord_metadata_service.restapi.description_utils import EXTRA_PROPERTIES, ontology_class


# If description and help are specified separately, the Django help text differs from the schema description. Otherwise,
# the data type is a string which fills both roles.

EXTERNAL_REFERENCE = {
    "description": "An encoding of information about a reference to an external resource.",
    "properties": {
        "id": "An application-specific identifier. It is RECOMMENDED that this is a CURIE that uniquely identifies the "
              "evidence source when combined with a resource; e.g. PMID:123456 with a resource `pmid`. It could also "
              "be a URI or other relevant identifier.",
        "description": "An application-specific free-text description.",
        **EXTRA_PROPERTIES
    }
}

UPDATE = {
    "description": "An update event for a record (e.g. a phenopacket.)",
    "properties": {
        "timestamp": {
            "description": "ISO8601 UTC timestamp specifying when when this update occurred.",
            "help": "Timestamp specifying when when this update occurred.",
        },
        "updated_by": "Information about the person/organization/network that performed the update.",
        "comment": "Free-text comment about the changes made and/or the reason for the update.",
        **EXTRA_PROPERTIES
    }
}

META_DATA = {
    "description": "A structured definition of the resources and ontologies used within a phenopacket.",
    "properties": {
        "created": {
            "description": "ISO8601 timestamp specifying when when this object was created.",
            "help": "Timestamp specifying when when this object was created.",
        },
        "created_by": "Name of the person who created the phenopacket.",
        "submitted_by": "Name of the person who submitted the phenopacket.",
        "resources": {
            "description": "A list of resources or ontologies referenced in the phenopacket",
            "items": RESOURCE
        },
        "updates": {
            "description": "A list of updates to the phenopacket.",
            "items": UPDATE
        },
        "phenopacket_schema_version": "Schema version of the current phenopacket.",
        "external_references": {
            "description": "A list of external (non-resource) references.",
            "items": EXTERNAL_REFERENCE
        },
        **EXTRA_PROPERTIES
    }
}

EVIDENCE = {
    "description": "A representation of the evidence for an assertion, such as an observation of a phenotypic feature.",
    "properties": {
        "evidence_code": ontology_class("that represents the evidence type"),
        "reference": EXTERNAL_REFERENCE,
        **EXTRA_PROPERTIES
    }
}


def phenotypic_feature(subject="a subject or biosample"):
    return {
        "description": f"A description of a phenotype that characterizes {subject} of a Phenopacket.",
        "properties": {
            "description": "Human-readable text describing the phenotypic feature; NOT for structured text.",
            "type": ontology_class("which describes the phenotype"),
            "negated": "Whether the feature is present (false) or absent (true, feature is negated); default is false.",
            "severity": ontology_class("that describes the severity of the condition"),
            "modifier": {  # TODO: Plural?
                "description": "A list of ontology terms that provide more expressive / precise descriptions of a "
                               "phenotypic feature, including e.g. positionality or external factors.",
                "items": ontology_class("that expounds on the phenotypic feature")
            },
            "onset": ontology_class("that describes the age at which the phenotypic feature was first noticed or "
                                    "diagnosed, e.g. HP:0003674"),
            "evidence": {
                "description": "One or more pieces of evidence that specify how the phenotype was determined.",
                "items": EVIDENCE,
            },
            **EXTRA_PROPERTIES
        }
    }


PHENOTYPIC_FEATURE = phenotypic_feature()


PROCEDURE = {
    "description": "A description of a clinical procedure performed on a subject in order to extract a biosample.",
    "properties": {
        "code": ontology_class("that represents a clinical procedure performed on a subject"),
        "body_site": ontology_class("that is specified when it is not possible to represent the procedure with a "
                                    "single ontology class"),
        **EXTRA_PROPERTIES
    }
}

HTS_FILE = {
    "description": "A link to a High-Throughput Sequencing (HTS) data file.",
    "properties": {
        "uri": "A valid URI to the file",
        "description": "Human-readable text describing the file.",
        "hts_format": "The file's format; one of SAM, BAM, CRAM, VCF, BCF, GVCF, FASTQ, or UNKNOWN.",
        "genome_assembly": "Genome assembly ID for the file, e.g. GRCh38.",
        "individual_to_sample_identifiers": ("Mapping between individual or biosample IDs and the sample identifier in "
                                             "the HTS file."),
        **EXTRA_PROPERTIES
    }
}

GENE = {
    "description": "A representation of an identifier for a gene.",
    "properties": {
        "id": "Official identifier of the gene. It SHOULD be a CURIE identifier with a prefix used by the official "
              "organism gene nomenclature committee, e.g. HGNC:347 for humans.",
        "alternate_ids": {
            "description": "A list of identifiers for alternative resources where the gene is used or catalogued.",
            "items": "An alternative identifier from a resource where the gene is used or catalogued."
        },
        "symbol": "A gene's official gene symbol as designated by the organism's gene nomenclature committee, e.g. "
                  "ETF1 from the HUGO Gene Nomenclature committee.",
        **EXTRA_PROPERTIES
    }
}

ALLELE = {
    "properties": {
        "id": "An arbitrary identifier.",
        "hgvs": "",
        "genome_assembly": "The reference genome identifier e.g. GRCh38.",
        "chr": "A chromosome identifier e.g. chr2 or 2.",
        "pos": "The 1-based genomic position e.g. 134327882.",
        "ref": "The reference base(s).",
        "alt": "The alternate base(s).",
        "info": "Relevant parts of the INFO field.",
        "seq_id": "Sequence ID, e.g. Seq1.",
        "position": "Position , a 0-based coordinate for where the Deleted Sequence starts, e.g. 4.",
        "deleted_sequence": "Deleted sequence , sequence for the deletion, can be empty, e.g. A",
        "inserted_sequence": "Inserted sequence , sequence for the insertion, can be empty, e.g. G",
        "iscn": "E.g. t(8;9;11)(q12;p24;p12)."
    }
}

VARIANT = {
    "description": "A representation used to describe candidate or diagnosed causative variants.",  # TODO: GA4GH VR
    "properties": {
        "allele": "The variant's corresponding allele",  # TODO: Allele data structure
        "zygosity": ontology_class("taken from the Genotype Ontology (GENO) representing the zygosity of the variant"),
        **EXTRA_PROPERTIES
    }
}

DISEASE = {
    "description": "A representation of a diagnosis, i.e. an inference or hypothesis about the cause underlying the "
                   "observed phenotypic abnormalities.",
    "properties": {
        "term": ontology_class("that represents the disease. It's recommended that one of the OMIM, Orphanet, or MONDO "
                               "ontologies is used for rare human diseases"),
        "onset": "A representation of the age of onset of the disease",  # TODO: Onset data structure
        "disease_stage": {
            "description": "A list of terms representing the disease stage. Elements should be derived from child "
                           "terms of NCIT:C28108 (Disease Stage Qualifier) or equivalent hierarchy from another "
                           "ontology.",
            "items": ontology_class("that represents the disease stage. Terms should be children of NCIT:C28108 "
                                    "(Disease Stage Qualifier) or equivalent hierarchy from another ontology"),
        },
        "tnm_finding": {
            "description": "A list of terms representing the tumour TNM score. Elements should be derived from child "
                           "terms of NCIT:C48232 (Cancer TNM Finding) or equivalent hierarchy from another "
                           "ontology.",
            "items": ontology_class("that represents the TNM score. Terms should be children of NCIT:C48232 "
                                    "(Cancer TNM Finding) or equivalent hierarchy from another ontology")
        },
        **EXTRA_PROPERTIES
    }
}


BIOSAMPLE = {
    "description": ("A unit of biological material from which the substrate molecules (e.g. genomic DNA, RNA, "
                    "proteins) for molecular analyses are extracted, e.g. a tissue biopsy. Biosamples may be shared "
                    "among several technical replicates or types of experiments."),
    "properties": {
        "id": "Unique arbitrary, researcher-specified identifier for the biosample.",
        "individual_id": "Identifier for the individual this biosample was sampled from.",
        "description": "Human-readable, unstructured text describing the biosample or providing additional "
                       "information.",
        "sampled_tissue": ontology_class("describing the tissue from which the specimen was collected. The use of "
                                         "UBERON is recommended"),
        "phenotypic_features": {
            "description": "A list of phenotypic features / abnormalities of the sample.",
            "items": phenotypic_feature("a biosample")
        },
        "taxonomy": ontology_class("specified when more than one organism may be studied. It is advised that codes"
                                   "from the NCBI Taxonomy resource are used, e.g. NCBITaxon:9606 for humans"),
        "individual_age_at_collection": None,  # TODO: oneOf
        "histological_diagnosis": ontology_class("representing a refinement of the clinical diagnosis. Normal samples "
                                                 "could be tagged with NCIT:C38757, representing a negative finding"),
        "tumor_progression": ontology_class("representing if the specimen is from a primary tumour, a metastasis, or a "
                                            "recurrence. There are multiple ways of representing this using ontology "
                                            "terms, and the terms chosen will have a specific meaning that is "
                                            "application specific"),
        "tumor_grade": ontology_class("representing the tumour grade. This should be a child term of NCIT:C28076 "
                                      "(Disease Grade Qualifier) or equivalent"),
        "diagnostic_markers": {
            "description": "A list of ontology terms representing clinically-relevant bio-markers.",
            "items": ontology_class("representing a clinically-relevant bio-marker. Most of the assays, such as "
                                    "immunohistochemistry (IHC), are covered by the NCIT ontology under the "
                                    "sub-hierarchy NCIT:C25294 (Laboratory Procedure), e.g. NCIT:C68748 "
                                    "(HER2/Neu Positive), or NCIT:C131711 Human Papillomavirus-18 Positive)")
        },
        "procedure": PROCEDURE,
        "hts_files": {
            "description": "A list of HTS files derived from the biosample.",
            "items": HTS_FILE
        },
        "variants": {
            "description": "A list of variants determined to be present in the biosample.",
            "items": VARIANT
        },
        "is_control_sample": "Whether the sample is being used as a normal control.",
        **EXTRA_PROPERTIES
    }
}


PHENOPACKET = {
    "description": "An anonymous phenotypic description of an individual or biosample with potential genes of interest "
                   "and/or diagnoses. The concept has multiple use-cases.",
    "properties": {
        "id": "Unique, arbitrary, researcher-specified identifier for the phenopacket.",
        "subject": INDIVIDUAL,  # TODO: Just phenopackets-specific components of individual?
        "phenotypic_features": {
            "description": "A list of phenotypic features observed in the proband.",
            "items": phenotypic_feature("the proband")
        },
        "biosamples": {
            "description": "Samples (e.g. biopsies) taken from the individual, if any.",
            "items": BIOSAMPLE
        },
        "genes": {
            "description": "Genes deemed to be relevant to the case; application-specific.",
            "items": GENE
        },
        "variants": {
            "description": "A list of variants identified in the proband.",
            "items": VARIANT
        },
        "diseases": {
            "description": "A list of diseases diagnosed in the proband.",
            "items": DISEASE
        },
        "hts_files": {
            "description": "A list of HTS files derived from the individual.",
            "items": HTS_FILE
        },
        "meta_data": META_DATA,
        **EXTRA_PROPERTIES
    }
}

# TODO: Mutually recursive, use functions
# DIAGNOSIS
# GENOMIC_INTERPRETATION
