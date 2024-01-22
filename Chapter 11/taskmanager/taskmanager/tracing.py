import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def init_tracing():
    jaeger_host = os.getenv("JAEGER_AGENT_HOST", "localhost")
    jaeger_port = int(os.getenv("JAEGER_AGENT_PORT", "4317"))
    jaeger_insecure = os.getenv("JAEGER_INSECURE", False)
    service_name = os.getenv("SERVICE_NAME", "taskmanager")

    resource = Resource(attributes={"service.name": service_name})

    trace.set_tracer_provider(TracerProvider(resource=resource))

    otlp_exporter = OTLPSpanExporter(
        endpoint=f"http://{jaeger_host}:{jaeger_port}", insecure=jaeger_insecure
    )

    span_processor = BatchSpanProcessor(otlp_exporter)

    trace.get_tracer_provider().add_span_processor(span_processor)

    DjangoInstrumentor().instrument()
