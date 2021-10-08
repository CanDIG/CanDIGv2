from django.conf import settings
from rest_framework.permissions import BasePermission, SAFE_METHODS


__all__ = [
    "ReadOnly",
    "OverrideOrSuperUserOnly",
]


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class OverrideOrSuperUserOnly(BasePermission):
    def has_permission(self, request, view):
        # If in CHORD production, is_superuser will be set by remote user headers.
        # TODO: Configuration: Allow configurable read-only APIs or other external access
        return settings.AUTH_OVERRIDE or request.user.is_superuser
