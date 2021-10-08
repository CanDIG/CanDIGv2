from chord_metadata_service.restapi.description_utils import EXTRA_PROPERTIES, ontology_class


EXPERIMENT = {
    "description": "Experiment related metadata.",
    "properties": {
        "id": "An arbitrary identifier for the experiment.",

        "reference_registry_id": "The IHEC EpiRR ID for this dataset, only for IHEC Reference Epigenome datasets. "
                                 "Otherwise leave empty.",
        "qc_flags": {
            "description": "Any quality control observations can be noted here. This field can be omitted if empty",
            "items": "A quality control observation.",
        },
        "experiment_type": "(Controlled Vocabulary) The assay target (e.g. ‘DNA Methylation’, ‘mRNA-Seq’, ‘smRNA-Seq’, "
                           "'Histone H3K4me1').",
        "experiment_ontology": {
            "description": "Links to experiment ontology information (e.g. via the OBI ontology.)",
            "items": ontology_class("describing the experiment"),
        },
        "molecule_ontology": {
            "description": "Links to molecule ontology information (e.g. via the SO ontology.)",
            "items": ontology_class("describing a molecular property"),
        },
        "molecule": "(Controlled Vocabulary) The type of molecule that was extracted from the biological material."
                    "Include one of the following: total RNA, polyA RNA, cytoplasmic RNA, nuclear RNA, small RNA, "
                    "genomic DNA, protein, or other.",
        "library_strategy": "(Controlled Vocabulary) The assay used. These are defined within the SRA metadata "
                            "specifications with a controlled vocabulary (e.g. ‘Bisulfite-Seq’, ‘RNA-Seq’, ‘ChIP-Seq’)."
                            " For a complete list, see https://www.ebi.ac.uk/ena/submit/reads-library-strategy.",

        "other_fields": "The other fields for the experiment.",

        "biosample": "Biosample on which this experiment was done.",

        **EXTRA_PROPERTIES
    }
}
