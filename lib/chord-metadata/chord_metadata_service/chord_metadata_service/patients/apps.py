from django.apps import AppConfig


class PatientsConfig(AppConfig):
    name = 'chord_metadata_service.patients'

    def ready(self):
        import chord_metadata_service.patients.signals  # noqa: F401
