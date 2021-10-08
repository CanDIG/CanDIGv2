"""metadata URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from chord_metadata_service.restapi import api_views, urls as restapi_urls
from chord_metadata_service.chord import urls as chord_urls
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.views import get_swagger_view

# TODO: django.conf.settings breaks reverse(), how to import properly?
from .settings import DEBUG

swagger_schema_view = get_swagger_view(title="Metadata Service API")
schema_view = get_schema_view(
    title="Metadata Service API",
    description="Metadata Service provides a phenotypic description of an Individual in the context of biomedical "
                "research.",
    version="0.1"
)

urlpatterns = [
    path('', swagger_schema_view),
    path('api/', include(restapi_urls)),
    path('api/schema', schema_view, name='openapi-schema'),
    path('service-info', api_views.service_info, name="service-info"),
    *chord_urls.urlpatterns,  # TODO: Use include? can we double up?
    *([path('admin/', admin.site.urls)] if DEBUG else []),
]
