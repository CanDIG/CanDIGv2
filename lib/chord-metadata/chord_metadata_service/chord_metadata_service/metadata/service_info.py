from .. import __version__
from .settings import CHORD_SERVICE_TYPE, CHORD_SERVICE_ID

# Service info according to spec https://github.com/ga4gh-discovery/ga4gh-service-info

SERVICE_INFO = {
    "id": CHORD_SERVICE_ID,
    "name": "Metadata Service",  # TODO: Globally unique?
    "type": CHORD_SERVICE_TYPE,
    "description": "Metadata service implementation based on Phenopackets schema",
    "organization": {
        "name": "C3G",
        "url": "http://www.computationalgenomics.ca"
    },
    "contactUrl": "mailto:ksenia.zaytseva@mcgill.ca",
    "version": __version__
}
