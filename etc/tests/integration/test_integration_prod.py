"""
Production-safe integration tests
Run with make test-integration-prod SITE_ADMIN_TOKEN=<token>
"""

import os
import sys
import authx.auth
import pytest
import requests

REPO_DIR = os.path.abspath(f"{os.path.dirname(os.path.realpath(__file__))}/../../..")
sys.path.insert(0, REPO_DIR)

from settings import get_env


ENV = get_env()

DEFAULT_TIMEOUT = 10

ENDPOINTS = {
    "htsget": f"{ENV['CANDIG_ENV']['TYK_HTSGET_API_LISTEN_PATH']}/htsget/v1/reads/service-info",
    "katsu": f"{ENV['CANDIG_ENV']['TYK_KATSU_API_LISTEN_PATH']}/v3/service-info",
    "rnaget": f"{ENV['CANDIG_ENV']['TYK_RNAGET_API_LISTEN_PATH']}/service-info",
    "federation": "federation/v1/service-info",
    "opa": f"{ENV['CANDIG_ENV']['TYK_OPA_API_LISTEN_PATH']}/v1/data/service/service-info",
    "query": f"{ENV['CANDIG_ENV']['TYK_QUERY_API_LISTEN_PATH']}/service-info",
    "candig-ingest": f"{ENV['CANDIG_ENV']['TYK_INGEST_API_LISTEN_PATH']}/service-info",
    "drs": "drs/ga4gh/drs/v1/service-info",
}


@pytest.fixture(scope="session", autouse=True)
def admin_token():
    """Get the site admin bearer token for the test session."""
    token = os.getenv("SITE_ADMIN_TOKEN", "").strip()
    if not token:
        pytest.exit("No admin token provided — aborting.", returncode=1)
    return token


def _auth_headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }


class TestInfrastructure:
    def test_keycloak(self):
        """Keycloak responds with valid configuration."""
        response = requests.get(
            f"{ENV['KEYCLOAK_PUBLIC_URL']}/auth/realms/{ENV['KEYCLOAK_REALM']}"
            "/.well-known/openid-configuration",
            timeout=DEFAULT_TIMEOUT,
        )
        assert response.status_code == 200
        assert "grant_types_supported" in response.json()

    def test_token_valid(self, admin_token):
        """Provided token is accepted by ingest service."""
        response = requests.get(
            f"{ENV['CANDIG_URL']}/ingest/service-info",
            headers=_auth_headers(admin_token),
            timeout=DEFAULT_TIMEOUT,
        )
        if response.status_code != 200:
            pytest.exit(
                f"Token validation failed (HTTP {response.status_code}) — stopping the rest of the tests.",
                returncode=1,
            )

    def test_tyk(self, admin_token):
        """All enabled modules return 200 valid JSON via the Tyk gateway."""
        modules = ENV["CANDIG_ENV"]["CANDIG_MODULES"].split()
        headers = _auth_headers(admin_token)
        results = {}
        for module in modules:
            if module not in ENDPOINTS:
                continue
            endpoint = ENDPOINTS[module]
            response = requests.get(
                f"{ENV['CANDIG_URL']}/{endpoint}",
                headers=headers,
                timeout=DEFAULT_TIMEOUT,
            )
            sc = response.status_code
            try:
                response.json()
            except requests.exceptions.JSONDecodeError:
                sc = 500
            results[endpoint] = sc
            print(f"  {endpoint}: {sc}")

        failed = [ep for ep, sc in results.items() if sc != 200]
        assert not failed, f"Tyk gateway returned non-200 for endpoints: {failed}"


class TestOPA:
    def test_policies_loaded(self, admin_token):
        """OPA policies return results."""
        for package in ("permissions", "service", "calculate"):
            response = requests.get(
                f"{ENV['CANDIG_URL']}/{ENV['CANDIG_ENV']['TYK_OPA_API_LISTEN_PATH']}/v1/data/{package}",
                headers=_auth_headers(admin_token),
                timeout=DEFAULT_TIMEOUT,
            )
            assert response.status_code == 200, f"OPA package '{package}' not queryable"
            assert "result" in response.json(), f"OPA package '{package}' returned no result"


class TestHtsget:
    def test_genes(self, admin_token):
        """htsget returns a list of genes."""
        response = requests.get(
            f"{ENV['CANDIG_URL']}/{ENV['CANDIG_ENV']['TYK_HTSGET_API_LISTEN_PATH']}/htsget/v1/genes",
            headers=_auth_headers(admin_token),
            timeout=DEFAULT_TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data, "genes response missing 'results' key"
        assert isinstance(data["results"], list), "'results' must be a list"

    def test_biosamples(self, admin_token):
        """htsget can retrieve genomic sample data via DRS."""
        response = requests.post(
            f"{ENV['CANDIG_URL']}/{ENV['CANDIG_ENV']['TYK_HTSGET_API_LISTEN_PATH']}/htsget/v1/biosamples",
            headers=_auth_headers(admin_token),
            json={},
            timeout=DEFAULT_TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "biosamples response must be a list"
        assert len(data) > 0, "no biosamples returned for admin user"
        for i, biosample in enumerate(data):
            assert "biosample_id" in biosample, f"biosample {i} missing 'biosample_id'"
            assert "program" in biosample, f"biosample {i} missing 'program'"


class TestKatsu:
    def test_programs(self, admin_token):
        """Katsu returns list of programs"""
        response = requests.get(
            f"{ENV['CANDIG_ENV']['KATSU_INGEST_URL']}/v3/authorized/programs/",
            headers=_auth_headers(admin_token),
            timeout=DEFAULT_TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("count", 0) > 0, "Katsu reports zero authorized programs"
        assert isinstance(data.get("items"), list), "Katsu 'items' must be a list"
        for i, program in enumerate(data["items"]):
            assert isinstance(program.get("program_id"), str) and program["program_id"], (
                f"Program {i} missing a non-empty 'program_id'"
            )

    def test_donors(self, admin_token):
        """Katsu returns list of donors"""
        response = requests.get(
            f"{ENV['CANDIG_ENV']['KATSU_INGEST_URL']}/v3/authorized/donors/",
            headers=_auth_headers(admin_token),
            timeout=DEFAULT_TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("count", 0) > 0, "Katsu reports zero authorized donors"
        assert isinstance(data.get("items"), list), "Katsu 'items' must be a list"
        for i, donor in enumerate(data["items"]):
            assert "submitter_donor_id" in donor, f"Donor {i} missing 'submitter_donor_id'"
            assert "program_id" in donor, f"Donor {i} missing 'program_id'"


class TestQuery:
    def test_discovery(self, admin_token):
        """Query discovery endpoint returns site-level summary"""
        response = requests.get(
            f"{ENV['CANDIG_ENV']['QUERY_INTERNAL_URL']}/discovery/programs",
            headers=_auth_headers(admin_token),
            timeout=DEFAULT_TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()
        assert "site" in data, "Query discovery missing 'site' key"

    def test_genomic_completeness(self, admin_token):
        """Query genomic_completeness returns completeness data for each program."""
        response = requests.get(
            f"{ENV['CANDIG_ENV']['QUERY_INTERNAL_URL']}/genomic_completeness",
            headers=_auth_headers(admin_token),
            timeout=DEFAULT_TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict) and len(data) > 0, (
            "genomic_completeness returned empty or non-dict"
        )
        for program_id, completeness in data.items():
            assert isinstance(program_id, str) and program_id, (
                "program_id must be non-empty string"
            )
            assert isinstance(completeness, dict), (
                f"completeness for '{program_id}' must be dict, got {type(completeness)}"
            )


    def test_search(self, admin_token):
        """Query search returns results and summary."""
        response = requests.get(
            f"{ENV['CANDIG_URL']}/{ENV['CANDIG_ENV']['TYK_QUERY_API_LISTEN_PATH']}/query",
            headers=_auth_headers(admin_token),
            params={},
            timeout=DEFAULT_TIMEOUT,
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data, f"Query response missing 'results': {list(data.keys())}"
        assert "summary" in data, f"Query response missing 'summary': {list(data.keys())}"
        assert isinstance(data["results"], list), "'results' must be a list"

    def test_katsu_and_query(self, admin_token):
        """Katsu authorized programs and query discovery programs align by program_id."""
        headers = _auth_headers(admin_token)

        katsu_resp = requests.get(
            f"{ENV['CANDIG_ENV']['KATSU_INGEST_URL']}/v3/authorized/programs/",
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
        )
        assert katsu_resp.status_code == 200
        katsu = katsu_resp.json()

        query_resp = requests.get(
            f"{ENV['CANDIG_ENV']['QUERY_INTERNAL_URL']}/discovery/programs",
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
        )
        assert query_resp.status_code == 200
        query = query_resp.json()

        katsu_programs = {
            p.get("program_id") for p in katsu.get("items", []) if p.get("program_id")
        }
        query_programs = {
            p.get("program_id")
            for p in query.get("programs", [])
            if p.get("program_id")
        }

        missing_in_query = katsu_programs - query_programs
        missing_in_katsu = query_programs - katsu_programs
        assert not missing_in_query and not missing_in_katsu, (
            f"Program lists differ: missing_in_query={missing_in_query}, missing_in_katsu={missing_in_katsu}"
        )


class TestFederation:
    def test_registry(self, admin_token):
        """Federation expected core services."""
        headers = _auth_headers(admin_token)

        servers_resp = requests.get(
            f"{ENV['CANDIG_URL']}/federation/v1/servers",
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
        )
        assert servers_resp.status_code == 200
        assert len(servers_resp.json()) > 0, "Federation registry has no servers"

        services_resp = requests.get(
            f"{ENV['CANDIG_URL']}/federation/v1/services",
            headers=headers,
            timeout=DEFAULT_TIMEOUT,
        )
        assert services_resp.status_code == 200
        service_ids = {svc["id"] for svc in services_resp.json()}
        expected = {"drs", "katsu", "htsget", "query"}
        missing = expected - service_ids
        assert not missing, f"Federation services registry missing: {missing}"

    @pytest.mark.parametrize(
        "service,path",
        [
            ("katsu", "v3/service-info"),
            ("htsget", "htsget/v1/reads/service-info"),
        ],
    )
    def test_fanout(self, admin_token, service, path):
        """Federation fanout works for local and federated modes."""
        headers_local = {**_auth_headers(admin_token), "federation": "false"}
        headers_federated = {**_auth_headers(admin_token), "federation": "true"}
        body = {
            "service": service,
            "method": "GET",
            "payload": {},
            "path": path,
        }

        # Test local fanout
        resp = requests.post(
            f"{ENV['CANDIG_URL']}/federation/v1/fanout",
            headers=headers_local,
            json=body,
            timeout=DEFAULT_TIMEOUT,
        )
        assert resp.status_code == 200
        assert "results" in resp.json()

        # Get expected number of federated servers
        expected_count = len(
            requests.get(
                f"{ENV['CANDIG_URL']}/federation/v1/servers",
                headers=_auth_headers(admin_token),
                timeout=DEFAULT_TIMEOUT,
            ).json()
        )

        # Test federated fanout
        resp = requests.post(
            f"{ENV['CANDIG_URL']}/federation/v1/fanout",
            headers=headers_federated,
            json=body,
            timeout=DEFAULT_TIMEOUT,
        )
        assert resp.status_code == 200
        results = resp.json()
        assert isinstance(results, list)
        assert "results" in results[0]
        assert len(results) == expected_count, (
            f"Expected {expected_count} federation results for {service}, got {len(results)}"
        )