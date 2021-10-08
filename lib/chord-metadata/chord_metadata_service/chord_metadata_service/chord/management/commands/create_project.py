from django.core.management.base import BaseCommand
from chord_metadata_service.chord.models import Project


class Command(BaseCommand):
    help = """
        Creates a Katsu/Bento project in the database.
        Arguments: "title" "description"
    """

    def add_arguments(self, parser):
        parser.add_argument("title", action="store", type=str, help="The title for the new project")
        parser.add_argument("description", action="store", type=str, help="The description for the new project")

    def handle(self, *args, **options):
        p = Project.objects.create(title=options["title"], description=options["description"])
        print("Project created:", p)
