import BASE_URL, {
  CHORD_METADATA_URL,
  FEDERATION_URL,
} from '../constants/constants';

function fetchIndividualsFederation(symptom) {
  if (!symptom || symptom.length === 0) {
    return fetch(FEDERATION_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        request_type: 'GET',
        endpoint_path: 'api/individuals?page_size=10000',
        endpoint_payload: {},
        endpoint_service: 'katsu',
      }),
    }).then((response) => {
      if (response.ok) {
        return response.json();
      }
      return {};
    });
  }

  return fetch(FEDERATION_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      request_type: 'GET',
      endpoint_path: `api/individuals?found_phenotypic_feature=${symptom}&page_size=10000`,
      endpoint_payload: {},
      endpoint_service: 'katsu',
    }),
  }).then((response) => {
    if (response.ok) {
      return response.json();
    }
    return {};
  });
}

function fetchIndividualsFederationWithParams(patientParams) {
  return fetch(FEDERATION_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      request_type: 'GET',
      endpoint_path: `api/individuals?${patientParams}`,
      endpoint_payload: {},
      endpoint_service: 'katsu',
    }),
  }).then((response) => {
    if (response.ok) {
      return response.json();
    }
    return {};
  });
}

/*
Fetch individuals from CHORD Metadata service and returns a promise
*/
function fetchIndividuals() {
  return fetch(`${CHORD_METADATA_URL}/api/individuals?page_size=10000`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  }).then((response) => {
    if (response.ok) {
      return response.json();
    }
    return {};
  });
}

/*
Fetch datasets from Federation Service endpoint and returns a promise
*/
function fetchDatasetsFederation() {
  return fetch(FEDERATION_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      request_type: 'POST',
      endpoint_path: 'datasets/search',
      endpoint_payload: {},
      endpoint_service: 'candig-server',
    }),
  }).then((response) => {
    if (response.ok) {
      return response.json();
    }
    return {};
  });
}

/*
Fetch servers from CanDIG web api datasets endpoint and returns a promise
*/
function fetchServers() {
  return fetchDatasetsFederation();
}

/*
Fetch counter for a specific Dataset Id; table; and field; and returns a promise
 * @param {string}... Dataset ID
 * @param {string}... Table to be fetched from
 * @param {list}... Field to be fetched from
*/
function getCountsFederation(datasetId, table, field) {
  let temp;
  if (!Array.isArray(field)) {
    temp = [field];
  } else {
    temp = field;
  }

  const payload = JSON.stringify({
    dataset_id: datasetId,
    logic: {
      id: 'A',
    },
    components: [
      {
        id: 'A',
        patients: {},
      },
    ],
    results: [
      {
        table,
        fields: temp,
      },
    ],
  });

  return fetch(FEDERATION_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      request_type: 'POST',
      endpoint_service: 'candig-server',
      endpoint_path: 'count',
      endpoint_payload: payload,
    }),
  }).then((response) => {
    if (response.ok) {
      return response.json();
    }
    return {};
  });
}

function searchVariantFederation(datasetId, start, end, referenceName) {
  return fetch(FEDERATION_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      request_type: 'POST',
      endpoint_path: 'variants/search',
      endpoint_payload: JSON.stringify({
        start,
        end,
        referenceName,
        datasetId,
      }),
      endpoint_service: 'candig-server',
    }),
  }).then((response) => {
    if (response.ok) {
      return response.json();
    }
    return {};
  });
}

/*
Fetch variant for a specific Dataset Id; start; and reference name; and returns a promise
 * @param {string}... Dataset ID
 * @param {number}... Start
 * @param {number}... End
 * @param {string}... Reference name
*/
function searchVariant(datasetId, start, end, referenceName) {
  return fetch(`${BASE_URL}/variants/search`, {
    method: 'post',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      start,
      end,
      referenceName,
      datasetId,
    }),
  }).then((response) => {
    if (response.ok) {
      return response.json();
    }
    return {};
  });
}

function searchSymptom(symptom) {
  if (!symptom || symptom.length === 0) {
    return {};
  }

  return fetch(FEDERATION_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      request_type: 'GET',
      endpoint_path: `api/phenopackets?found_phenotypic_feature=${symptom}&page_size=10000`,
      endpoint_payload: {},
      endpoint_service: 'katsu',
    }),
  }).then((response) => {
    if (response.ok) {
      return response.json();
    }
    return {};
  });
}

export {
  fetchIndividuals,
  fetchIndividualsFederation,
  fetchIndividualsFederationWithParams,
  fetchDatasetsFederation,
  getCountsFederation,
  searchVariantFederation,
  fetchServers,
  searchVariant,
  searchSymptom,
};
