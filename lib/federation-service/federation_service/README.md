# federation_service
Microservice implementation of federation code from CanDIG v1 for CanDIG v2

Based on CanDIG demo projects: [OpenAPI variant service demo](https://github.com/ljdursi/openapi_calls_example), [Python Model Service](https://github.com/CanDIG/python_model_service).


## Stack

- [Connexion](https://github.com/zalando/connexion) for implementing the API
- [Bravado-core](https://github.com/Yelp/bravado-core) for Python classes from the spec
- Python 3
- Pytest

## Installation

The federation_service can be installed in a py3.7+ virtual environment:

```
pip install -r requirements.txt
```

## Configuration Files

The federation_service requires two JSON configuration files to be
placed into the `federation_service/configs` directory. These files are
a peers.json and a services.json file following the peers_ex.json 
and services_ex.json examples provided in the configs folder

#### Peers

Peer nodes 

### Running

The service can be started with:

```
python -m candig_federation
```

If wanting to run multiple nodes on the same network, create different
service configs and specify them at runtime:

```
python -m candig_federation --host 0.0.0.0 --port 4232 --services ./configs/service_name.json
```

Once the service is running, a Swagger UI can be accessed at : `/federation/ui`


### Testing

Tests can be run with pytest and coverage:

```pytest --cov=candig_federation tests/```
