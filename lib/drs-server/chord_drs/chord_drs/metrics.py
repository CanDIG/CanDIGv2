from prometheus_flask_exporter import PrometheusMetrics

__all__ = ["metrics"]

metrics = PrometheusMetrics.for_app_factory()
