import json
import os


__all__ = ["EXAMPLE_INGEST_PHENOPACKET", "EXAMPLE_INGEST_OUTPUTS"]

with open(os.path.join(os.path.dirname(__file__), "example_phenopacket.json"), "r") as pf:
    EXAMPLE_INGEST_PHENOPACKET = json.load(pf)

EXAMPLE_INGEST_OUTPUTS = {
    "json_document": os.path.join(os.path.dirname(__file__), "example_phenopacket.json"),
}
