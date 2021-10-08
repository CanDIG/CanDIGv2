changes to DATS:

1. extension of license to allow provision of annotation codes for the following:
	a. consent information code/term
	b. terms of use code/term
	c. extension range to apply to Dimension,Material,Software,StudyGroup in addition to Dataset
	d. addition of 'dates' to specify any relevant timestamp information
		"dates" : {
	      "description": "Relevant dates, the date of the license may be provided.",
	      "type" : "array",
	      "items": {
	        "$ref" : "date_info_schema.json#"
	      }
	    }, 

2. extension by creation of a new schema to support GenomicLocation
	a. same as the one developed by AGR [https://github.com/alliance-genome/agr_schemas/blob/develop/gene/genomeLocation.json]
	b. added to Material and MolecularEntity object

3. extension of DATS.molecular_entity_schema to include:
	a. addition of 'dates' element: 
		-rationale: report any relevant timestamp that may be associated with the entity. For example, report on a object creation date or annotation date.

		"dates" : {
	      "description": "Relevant dates for the datasets, a date must be added, e.g. creation date or last modification date should be added.",
	      "type" : "array",
	      "items" : {
	        "$ref" : "date_info_schema.json#"
	      }
	    },

    b. addition of 'genomicLocations' element
		-rationale: report any positional information for genome based dataset (.e.g AGR).

	    "genomeLocations" : {
	      "description": "The set of location information of a genetic element in a genome.",
	      "type" : "array",
	      "items" : {
	          "$ref": "genome_location_schema.json#"     
	      }
	    }

	c. addition of 'relatedEntity' element (2 options are provided for review and discussion) and creation a new schema: related_entity_schema.json
		-rationale: report any information about association of a MolecularEntity with other entities, other Molecular Entites, Material Entities, Disease 

		"relatedEntities": {
		      "description": "Related molecular entities.",
		      "type": "array",
		      "items": {
		        "$ref": "molecular_entity_schema.json#",
		        "relationType": {
		          "description": "The type of the relationship corresponding to this molecular entity.",
		          "type" : "string",
		          "format": "uri"
		        }
		      }
		    },

		    TODO: more thoughts and testing to finalize this addition


	d. addition of 'involvedInProcess' element:
		-rationale: allow proper casting of GO process annotation (other GO categories, Function and Molecular Compoment can be set to 'Roles' and @type, GO process was left out in the cold

		"involvedInProcess" : {
	      "description": "the molecular processes where the molecular entity is known to be involved",
	      "type": "array",
	      "items":{
	        "$ref" : "activity.json#"
	      }
	    }

	  NOTE: material_schema.json currently defines a "involvedInBiologicalEntity" (where the current DATS documentation seems to imply the Biological Entity to be a process)

4. extension to License, Grant, MolecularEntity,Material Entities, Software, Disease, with 'dates' element

		-rationale: make it easier to attach dates to entities
		-caveat: generic typing is not possible and json-ld context file can not be used to provide more specificity. case by case tuning when writing import will be needed when attempting harmonization

		"dates" : {
	      "description": "Relevant dates, the date of the license may be provided.",
	      "type" : "array",
	      "items": {
	        "$ref" : "date_info_schema.json#"
	      }
	    }, 

5. Adding Licenses attribute to StudyGroup, Dimension, Material.
		-rationale: allow both granular or blanket specification of terms of use for both Variables (e.g. query-case= can I use this data ? ) and Materials (e.g.query-case= am I allowed to obtain a specimen for my research? )






