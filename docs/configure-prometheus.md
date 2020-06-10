# Configuring Prometheus

## For Flask Applications

In order to expose the `/metrics` endpoint of Flask Application, the below steps must be followed:

- Install `prometheus_flask_exporter` library from Pypi
- On the file where you instantiate your Flask app, import `PrometheusMetrics` and add your app:
```python
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)
```

That’s really it! By adding an import and a line to initialize PrometheusMetrics you’ll get request duration metrics and request counters exposed on the `/metrics` endpoint of the Flask application it’s registered on.

These are the basics configuration, for more information please visit Prometheus Flask exporter Github's [page](https://github.com/rycus86/prometheus_flask_exporter)


## For DJango Applications

In order to expose the `/metrics` endpoint of DJango Application, the below steps must be followed:

- Install `django-prometheus` library from Pypi
- In your `settings.py`:
```python
INSTALLED_APPS = (
   ...
   'django_prometheus',
   ...
)

MIDDLEWARE_CLASSES = (
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # All your other middlewares go here, including the default
    # middlewares like SessionMiddleware, CommonMiddleware,
    # CsrfViewmiddleware, SecurityMiddleware, etc.
    'django_prometheus.middleware.PrometheusAfterMiddleware',
)
```

In your `urls.py`:
```python
urlpatterns = [
    ...
    path('', include('django_prometheus.urls')),
]
```

By adding middlewares and an url you’ll get request duration metrics and request counters exposed on the /metrics endpoint of the DJango application.

These are the basics configuration, for more information please visit django-prometheus Github's [webpage](https://github.com/korfuri/django-prometheus)
