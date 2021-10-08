# datasets_service
Microservice implementation of Datasets from CanDIG v1 for CanDIG v2

Based on CanDIG demo projects: [OpenAPI variant service demo](https://github.com/ljdursi/openapi_calls_example), [Python Model Service](https://github.com/CanDIG/python_model_service).


## Stack

- [Connexion](https://github.com/zalando/connexion) for implementing the API
- [Bravado-core](https://github.com/Yelp/bravado-core) for Python classes from the spec
- Python 3
- Pytest

## Installation

The datasets_service can be installed in a py3.7+ virtual environment:

```
pip install -r requirements.txt
```



### Running

The service can be started with:

```
python -m candig_dataset_service
```

If wanting to run multiple nodes on the same network, create different
service configs and specify them at runtime:

```
python -m candig_dataset_service --host 0.0.0.0 --port 4232 --logfile ./log/newlog.log
```

Once the service is running, a Swagger UI can be accessed at : `/v2/`


### Testing

Tests can be run with pytest and coverage:

```pytest --cov=candig_datasets tests/```
