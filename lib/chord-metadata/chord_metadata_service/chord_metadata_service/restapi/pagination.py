from django.conf import settings
from rest_framework import pagination
from urllib.parse import urljoin


__all__ = [
    "LargeResultsSetPagination",
]


class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 10000

    # Fix next/previous links inside sub-path-mounted reverse proxies in the CHORD context:

    def _get_chord_absolute_uri(self):
        full_path = self.request.get_full_path()
        # Strip first slash if necessary, to avoid urljoin removing reverse proxy sub-paths
        if len(full_path) > 0 and full_path[0] == "/":
            full_path = full_path[1:]
        return urljoin(settings.CHORD_URL, full_path)

    def get_next_link(self):
        if settings.CHORD_URL is not None:
            # Monkey-patch rewrite build_absolute_uri
            self.request.build_absolute_uri = self._get_chord_absolute_uri
        return super(LargeResultsSetPagination, self).get_next_link()

    def get_previous_link(self):
        if settings.CHORD_URL is not None:
            # Monkey-patch rewrite build_absolute_uri
            self.request.build_absolute_uri = self._get_chord_absolute_uri
        return super(LargeResultsSetPagination, self).get_previous_link()

    def get_html_context(self):
        if settings.CHORD_URL is not None:
            # Monkey-patch rewrite build_absolute_uri
            self.request.build_absolute_uri = self._get_chord_absolute_uri
        super(LargeResultsSetPagination, self).get_html_context()
