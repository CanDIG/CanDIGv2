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


from chord_metadata_service.restapi.description_utils import EXTRA_PROPERTIES


__all__ = ["RESOURCE"]


RESOURCE = {
    "description": "A description of an external resource used for referencing an object.",
    "properties": {
        "id": {
            "description": "Unique researcher-specified identifier for the resource.",
            "help": "For OBO ontologies, the value of this string MUST always be the official OBO ID, which is always "
                    "equivalent to the ID prefix in lower case. For other resources use the prefix in "
                    "identifiers.org."
        },
        "name": {
            "description": "Human-readable name for the resource.",
            "help": "The full name of the resource or ontology referred to by the id element."
        },
        "namespace_prefix": "Prefix for objects from this resource. In the case of ontology resources, this should be "
                            "the CURIE prefix.",
        "url": "Resource URL. In the case of ontologies, this should be an OBO or OWL file. Other resources should "
               "link to the official or top-level url.",
        "version": "The version of the resource or ontology used to make the annotation.",
        "iri_prefix":  "The IRI prefix, when used with the namespace prefix and an object ID, should resolve the term "
                       "or object from the resource in question.",
        **EXTRA_PROPERTIES
    }
}
