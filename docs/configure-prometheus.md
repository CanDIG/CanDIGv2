# Configuring Prometheus

Before configuring the APIs we first need to tell Prometheus which services to monitor. Prometheus collects metrics from monitored targets by scraping metrics HTTP endpoints on these targets. 

In order to do that, each service must be added to the `scrape_configs` section on `prometheus.yml` file under `bin\prometheus` (make sure you have downloaded Prometheus by running the command `make bin-prometheus` first). Here is an example:
```yml
scrape_configs:
  # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
  - job_name: 'cnv_service'

    # Override the global default and scrape targets from this job every 5 seconds.
    scrape_interval: 5s

    static_configs:
      - targets: ['127.0.0.0:3000']
```

The above example will configure Prometheus to monitor the service running on http//127.0.0.0:3000 by reading its `/metrics` endpoint.

You can read more about how to configure Prometheus at Prometheus' [webpage](https://prometheus.io/docs/prometheus/latest/getting_started/).

To set the `/metrics` endpoint each framework has its own way on configuring it. Above we describe how configure it using Flask and DJango frameworks.

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
