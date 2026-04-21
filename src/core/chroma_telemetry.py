"""No-op telemetry client for local Chroma usage."""
from chromadb.telemetry.product import ProductTelemetryClient, ProductTelemetryEvent
from overrides import override


class NoOpTelemetryClient(ProductTelemetryClient):
    """Disable Chroma product telemetry entirely."""

    @override
    def capture(self, event: ProductTelemetryEvent) -> None:
        return None
