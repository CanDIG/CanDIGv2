from django.apps import AppConfig


class PhenopacketsConfig(AppConfig):
    name = 'chord_metadata_service.phenopackets'

    def ready(self):
        import chord_metadata_service.phenopackets.signals  # noqa: F401
