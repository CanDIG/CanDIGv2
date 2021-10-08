from . import models, schemas
from chord_metadata_service.patients.schemas import INDIVIDUAL_SCHEMA
from chord_metadata_service.resources.search_schemas import RESOURCE_SEARCH_SCHEMA
from chord_metadata_service.restapi.schema_utils import (
    merge_schema_dictionaries,
    search_optional_eq,
    search_optional_str,
    tag_schema_with_search_properties,
)
from chord_metadata_service.restapi.search_schemas import ONTOLOGY_SEARCH_SCHEMA

__all__ = [
    "EXTERNAL_REFERENCE_SEARCH_SCHEMA",
    "PHENOPACKET_SEARCH_SCHEMA",
]


# TODO: Rewrite and use
def _tag_with_database_attrs(schema: dict, db_attrs: dict):
    return {
        **schema,
        "search": {
            **schema.get("search", {}),
            "database": {
                **schema.get("search", {}).get("database", {}),
                **db_attrs
            }
        }
    }


EXTERNAL_REFERENCE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA, {
    "properties": {
        "id": {
            "search": search_optional_str(0)
        },
        "description": {
            "search": search_optional_str(1, multiple=True)  # TODO: Searchable? may leak
        }
    },
    "search": {
        "database": {
            "type": "jsonb"  # TODO: parameterize?
        }
    }
})

INDIVIDUAL_SEARCH_SCHEMA = tag_schema_with_search_properties(INDIVIDUAL_SCHEMA, {
    "properties": {
        "id": {
            "search": {
                **search_optional_eq(0, queryable="internal"),
                "database": {
                    "field": models.Individual._meta.pk.column
                }
            }
        },
        "alternate_ids": {
            "items": {
                "search": search_optional_str(0, queryable="internal", multiple=True)
            },
            "search": {
                "database": {
                    "type": "array"
                }
            }
        },
        "date_of_birth": {
            # TODO: Internal?
            # TODO: Allow lt / gt
            "search": search_optional_eq(1, queryable="internal")
        },
        # TODO: Age
        "sex": {
            "search": search_optional_eq(2)
        },
        "karyotypic_sex": {
            "search": search_optional_eq(3)
        },
        "taxonomy": ONTOLOGY_SEARCH_SCHEMA,
    },
    "search": {
        "database": {
            "relation": models.Individual._meta.db_table,
            "primary_key": models.Individual._meta.pk.column,
        }
    },
})

UPDATE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_UPDATE_SCHEMA, {
    "properties": {
        # TODO: timestamp
        "updated_by": {
            "search": search_optional_str(0, multiple=True),
        },
        "comment": {
            "search": search_optional_str(1, multiple=True),
        }
    },
    "search": {
        "database": {
            "type": "jsonb"
        }
    }
})

# noinspection PyProtectedMember
META_DATA_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_META_DATA_SCHEMA, {
    "properties": {
        # TODO: created
        "created_by": {
            "search": search_optional_str(0, multiple=True),
        },
        "submitted_by": {
            "search": search_optional_str(1, multiple=True),
        },
        "resources": {
            "items": RESOURCE_SEARCH_SCHEMA,
            "search": {
                "database": {
                    "relation": models.MetaData._meta.get_field("resources").remote_field.through._meta.db_table,
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "metadata_id",  # TODO: No hard-code
                        "parent_primary_key": models.MetaData._meta.pk.column  # TODO: Redundant?
                    }
                }
            }
        },
        "updates": {
            "items": UPDATE_SEARCH_SCHEMA,
            "search": {
                "database": {
                    "type": "array"
                }
            }
        },
        # TODO: phenopacket_schema_version
        "external_references": {
            "items": EXTERNAL_REFERENCE_SEARCH_SCHEMA
        }
    },
    "search": {
        "database": {
            "relation": models.MetaData._meta.db_table,
            "primary_key": models.MetaData._meta.pk.column
        }
    }
})

EVIDENCE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_EVIDENCE_SCHEMA, {
    "properties": {
        "evidence_code": ONTOLOGY_SEARCH_SCHEMA,
        "reference": EXTERNAL_REFERENCE_SEARCH_SCHEMA,
    },
    "search": {
        "database": {
            "type": "jsonb"
        }
    }
})

PHENOTYPIC_FEATURE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA, {
    "properties": {
        "description": {
            "search": search_optional_str(0, multiple=True),  # TODO: Searchable? may leak
        },
        "type": merge_schema_dictionaries(ONTOLOGY_SEARCH_SCHEMA, {
            "search": {
                "database": {
                    # Due to conflict with a Python top-level function,
                    # type is pftype in the database and is overridden here.
                    "field": "pftype"
                }
            }
        }),
        "negated": {
            "search": search_optional_eq(1),
        },
        "severity": ONTOLOGY_SEARCH_SCHEMA,
        "modifier": {  # TODO: Plural?
            "items": ONTOLOGY_SEARCH_SCHEMA
        },
        "onset": ONTOLOGY_SEARCH_SCHEMA,
        "evidence": EVIDENCE_SEARCH_SCHEMA,
    },
    "search": {
        "database": {
            "relation": models.PhenotypicFeature._meta.db_table,
            "primary_key": models.PhenotypicFeature._meta.pk.column
        }
    }
})

# TODO: Fix
GENE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_GENE_SCHEMA, {
    "properties": {
        "id": {
            "search": search_optional_str(0),
        },
        "alternate_ids": {
            "items": {
                "search": search_optional_str(1),
            }
        },
        "symbol": {
            "search": search_optional_str(2),
        }
    },
    "search": {
        "database": {
            "relation": models.Gene._meta.db_table,
            "primary_key": models.Gene._meta.pk.column
        }
    }
})

# TODO: Search? Probably not
HTS_FILE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_HTS_FILE_SCHEMA, {})

# TODO: search??
VARIANT_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_VARIANT_SCHEMA, {
    "properties": {
        "allele": {"search": {}},  # TODO
        "zygosity": ONTOLOGY_SEARCH_SCHEMA,
    }
})

BIOSAMPLE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_BIOSAMPLE_SCHEMA, {
    "properties": {
        "id": {
            "search": merge_schema_dictionaries(
                search_optional_eq(0, queryable="internal"),
                {"database": {"field": models.Biosample._meta.pk.column}}
            )
        },
        "individual_id": {  # TODO: Does this work?
            "search": search_optional_eq(1, queryable="internal"),
        },
        "description": {
            "search": search_optional_str(2, multiple=True),  # TODO: Searchable? may leak
        },
        "sampled_tissue": ONTOLOGY_SEARCH_SCHEMA,
        "phenotypic_features": {
            "items": merge_schema_dictionaries(
                PHENOTYPIC_FEATURE_SEARCH_SCHEMA,
                {"search": {"database": {
                    "relationship": {
                        "type": "MANY_TO_ONE",
                        "foreign_key": "phenotypicfeature_id"  # TODO: No hard-code, from M2M
                    }
                }}}
            ),
            "search": merge_schema_dictionaries(
                PHENOTYPIC_FEATURE_SEARCH_SCHEMA["search"],
                {"database": {
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": models.PhenotypicFeature._meta.get_field("biosample").column,
                        "parent_primary_key": models.Biosample._meta.pk.column  # TODO: Redundant
                    }
                }}
            )
        },
        "taxonomy": ONTOLOGY_SEARCH_SCHEMA,
        # TODO: Front end will need to deal with this:
        # TODO: individual_age_at_collection
        "histological_diagnosis": ONTOLOGY_SEARCH_SCHEMA,
        "tumor_progression": ONTOLOGY_SEARCH_SCHEMA,
        "tumor_grade": ONTOLOGY_SEARCH_SCHEMA,  # TODO: Is this a list?
        "diagnostic_markers": {
            "items": ONTOLOGY_SEARCH_SCHEMA,
            "search": {"database": {"type": "array"}}
        },
        "procedure": {
            "properties": {
                "code": ONTOLOGY_SEARCH_SCHEMA,
                "body_site": ONTOLOGY_SEARCH_SCHEMA
            },
            "search": {
                "database": {
                    "primary_key": models.Procedure._meta.pk.column,
                    "relation": models.Procedure._meta.db_table,
                    "relationship": {
                        "type": "MANY_TO_ONE",
                        "foreign_key": models.Biosample._meta.get_field("procedure").column
                    }
                }
            }
        },
        "hts_files": {
            "items": HTS_FILE_SEARCH_SCHEMA  # TODO
        },
        "variants": {
            "items": VARIANT_SEARCH_SCHEMA,  # TODO: search?
        },
        "is_control_sample": {
            "search": search_optional_eq(1),  # TODO: Boolean search
        },
    },
    "search": {
        "database": {
            "primary_key": models.Biosample._meta.pk.column,
            "relation": models.Biosample._meta.db_table,
        }
    }
})

# TODO
DISEASE_ONSET_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_DISEASE_ONSET_SCHEMA, {})

DISEASE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_DISEASE_SCHEMA, {
    "properties": {
        "term": ONTOLOGY_SEARCH_SCHEMA,
        "onset": DISEASE_ONSET_SEARCH_SCHEMA,
        "disease_stage": {
            "items": ONTOLOGY_SEARCH_SCHEMA,
            "search": {"database": {"type": "array"}}
        },
        "tnm_finding": {
            "items": ONTOLOGY_SEARCH_SCHEMA,
            "search": {"database": {"type": "array"}}
        },
    },
    "search": {
        "database": {
            "primary_key": models.Disease._meta.pk.column,
            "relation": models.Disease._meta.db_table,
        }
    }
})

# noinspection PyProtectedMember
PHENOPACKET_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.PHENOPACKET_SCHEMA, {
    "properties": {
        "id": {
            "search": {"database": {"field": models.Phenopacket._meta.pk.column}}
        },
        "subject": merge_schema_dictionaries(
            INDIVIDUAL_SEARCH_SCHEMA,
            {"search": {"database": {
                "relationship": {
                    "type": "MANY_TO_ONE",
                    "foreign_key": models.Phenopacket._meta.get_field("subject").column
                }
            }}}),
        "phenotypic_features": {
            "items": merge_schema_dictionaries(
                PHENOTYPIC_FEATURE_SEARCH_SCHEMA,
                {"search": {"database": {
                    "relationship": {
                        "type": "MANY_TO_ONE",
                        "foreign_key": models.PhenotypicFeature._meta.pk.column
                    }
                }}}),
            "search": merge_schema_dictionaries(
                PHENOTYPIC_FEATURE_SEARCH_SCHEMA["search"],
                {"database": {
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "phenopacket_id",  # TODO: No hard-code
                        "parent_primary_key": models.Phenopacket._meta.pk.column  # TODO: Redundant?
                    }
                }})
        },
        "biosamples": {
            "items": merge_schema_dictionaries(
                BIOSAMPLE_SEARCH_SCHEMA,
                {"search": {"database": {
                    "relationship": {
                        "type": "MANY_TO_ONE",
                        "foreign_key": "biosample_id"  # TODO: No hard-code, from M2M
                    }
                }}}),
            "search": {
                "database": {
                    "relation": models.Phenopacket._meta.get_field("biosamples").remote_field.through._meta.db_table,
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "phenopacket_id",  # TODO: No hard-code
                        "parent_primary_key": models.Phenopacket._meta.pk.column  # TODO: Redundant?
                    }
                }
            }
        },
        "genes": {  # TODO: Too sensitive for search?
            "items": merge_schema_dictionaries(
                GENE_SEARCH_SCHEMA,
                {"search": {"database": {
                    "relationship": {
                        "type": "MANY_TO_ONE",
                        "foreign_key": "gene_id"
                    }}}}),
            "search": {
                "database": {
                    "relation": models.Phenopacket._meta.get_field("genes").remote_field.through._meta.db_table,
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "phenopacket_id",  # TODO: No hard-code
                        "parent_primary_key": models.Phenopacket._meta.pk.column  # TODO: Redundant?
                    }
                }
            }
        },
        "variants": {
            "items": VARIANT_SEARCH_SCHEMA
        },
        "diseases": {  # TODO: Too sensitive for search?
            "items": merge_schema_dictionaries(
                DISEASE_SEARCH_SCHEMA,
                {"search": {"database": {
                    "relationship": {
                        "type": "MANY_TO_ONE",
                        "foreign_key": "disease_id"  # TODO: No hard-code, from M2M
                    }}}}),
            "search": {
                "database": {
                    "relation": models.Phenopacket._meta.get_field("diseases").remote_field.through._meta.db_table,
                    "relationship": {
                        "type": "ONE_TO_MANY",
                        "parent_foreign_key": "phenopacket_id",  # TODO: No hard-code
                        "parent_primary_key": models.Phenopacket._meta.pk.column  # TODO: Redundant?
                    }
                }
            }
        },  # TODO
        "hts_files": {
            "items": HTS_FILE_SEARCH_SCHEMA  # TODO
        },
        "meta_data": META_DATA_SEARCH_SCHEMA
    },
    "search": {
        "database": {
            "relation": models.Phenopacket._meta.db_table,
            "primary_key": models.Phenopacket._meta.pk.column
        }
    }
})
