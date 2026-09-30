"""Industrial RFQ Intelligence Python package namespace.\n\nThe implementation package path remains ``freellmpool`` for backward\ncompatibility with the existing codebase. The repository and product identity\nare ``industrial-rfq-intelligence``; industrial RFQ functionality lives under\nthis compatibility namespace while package-path cleanup is handled separately.\n\nLegacy pool/provider APIs remain available to avoid breaking existing imports.\n"""

from ._version import __version__
from .errors import (
    AllProvidersExhausted,
    ContextWindowExceeded,
    FreeLLMPoolError,
    NoProvidersConfigured,
)
from .metrics import Metrics
from .models import EmbedReply, Model, Provider, Reply
from .plugins import register_adapter, register_provider
from .router import Pool


def __getattr__(name: str):
    # Lazy so importing freellmpool never imports the async stack (httpx.AsyncClient)
    # unless someone actually asks for AsyncPool.
    if name == "AsyncPool":
        from .aio import AsyncPool

        return AsyncPool
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "Pool",
    "AsyncPool",
    "Provider",
    "Model",
    "Reply",
    "EmbedReply",
    "Metrics",
    "register_provider",
    "register_adapter",
    "FreeLLMPoolError",
    "NoProvidersConfigured",
    "AllProvidersExhausted",
    "ContextWindowExceeded",
    "__version__",
]
