import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def initialize_tracing(service_name: str = "adk-ide-service") -> Optional[str]:
    """Initialize OpenTelemetry tracing with OTLP exporter if configured.

    Returns an error string if setup fails, otherwise None.
    """
    try:
        otlp_endpoint = os.environ.get("OTLP_TRACES_ENDPOINT")
        if not otlp_endpoint:
            # Tracing disabled unless endpoint provided
            return None

        headers = {}
        if os.environ.get("OTLP_TRACES_API_KEY"):
            headers["api-key"] = os.environ["OTLP_TRACES_API_KEY"]

        provider = TracerProvider()
        trace.set_tracer_provider(provider)

        exporter = OTLPSpanExporter(endpoint=otlp_endpoint, headers=headers)
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)

        # Set service name attribute if OTLP backend supports resource attrs via env
        os.environ.setdefault("OTEL_SERVICE_NAME", service_name)

        return None
    except Exception as exc:  # pragma: no cover
        return str(exc)

