# Configuring Prometheus

## For Flask Applications

In order to expose the `/metrics`  endpoint of Flask Application, the below steps must be followed:

- Install `prometheus_flask_exporter` library from Pypi
- On the file where you instantiate your Flask app, import `PrometheusMetrics` and add your app:
```python
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)
```

That’s really it! By adding an import and a line to initialize PrometheusMetrics you’ll get request duration metrics and request counters exposed on the `/metrics` endpoint of the Flask application it’s registered on
