from django.conf import settings
from django.http import HttpResponseForbidden
import jwt
import requests


# TODO: replace this hacky stuff with more robust solution
APPLICABLE_ENDPOINTS = frozenset({
    '/api/individuals',
    '/api/diseases',
    '/api/phenotypicfeatures'
})


class CandigAuthzMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.INSIDE_CANDIG and self.is_applicable_endpoint(request):
            # TODO: So currently I'm assuming the frontend will query the
            # dataset info beforehand so as to be able to include it here
            # so we know which authz rule to apply
            # Bit clumsy, consider this a stop-gap measure
            access_level = self.decode_permissions(request)

            if not access_level:
                return HttpResponseForbidden()

            try:
                allowed = self.query_opa(request, access_level)
            except requests.exceptions.RequestException:
                return HttpResponseForbidden()

            if not allowed:
                return HttpResponseForbidden()

        return self.get_response(request)

    def is_applicable_endpoint(self, request):
        return request.path in APPLICABLE_ENDPOINTS

    def decode_permissions(self, request):
        if 'X-CanDIG-Dataset' not in request.headers:
            return
        else:
            dataset = request.headers.get('X-CanDIG-Dataset')

        if 'X-CanDIG-Authz' in request.headers:
            authz_jwt = request.headers.get("X-CanDIG-Authz").split(' ')[1]
            # TODO: yes it is a terrible idea to decode without checking the
            # the signature, gotta find a proper way to transmit vault's public key
            decoded_jwt = jwt.decode(authz_jwt, verify=False)

            if 'permissions' in decoded_jwt:
                permissions = decoded_jwt.get('permissions')

                # TODO: I am assuming the permission object is a simple dict such as
                # {"DATASET_NAME": 4}
                # TODO: would make sense to package this feature, the reading of the
                # permission object in a lib, since we'll repeat that stuff over many services
                if dataset in permissions:
                    return permissions[dataset]
                else:
                    return

    def query_opa(self, request, access_level):
        if not settings.CANDIG_OPA_URL:
            return False

        params = {
            "input": {
                "path": request.path,
                "method": request.method,
                "access_level": int(access_level)
            }
        }

        url = f"{settings.CANDIG_OPA_URL}/v1/data/metadata"

        res = requests.post(url, json=params)
        res.raise_for_status()

        data = res.json()

        return data.get('result', {}).get('allow', False)
