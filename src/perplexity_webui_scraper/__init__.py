"""Extract AI responses from Perplexity's web interface."""

from importlib import metadata

from .config import ClientConfig, ConversationConfig
from .core import Conversation, Perplexity
from .exceptions import (
    AuthenticationError,
    FileUploadError,
    FileValidationError,
    HTTPError,
    PerplexityError,
    RateLimitError,
    ResearchClarifyingQuestionsError,
    ResponseParsingError,
    StreamingError,
)
from .models import MODELS, Model
from .types import (
    CitationMode,
    Coordinates,
    FileInput,
    LogLevel,
    Response,
    SearchFocus,
    SearchResultItem,
    SourceFocus,
    TimeRange,
)


ConversationConfig.model_rebuild()


try:
    __version__: str = metadata.version("perplexity-webui-scraper")
except Exception:
    __version__: str = "0.0.0-local"
__all__: list[str] = [
    "MODELS",
    "AuthenticationError",
    "CitationMode",
    "ClientConfig",
    "Conversation",
    "ConversationConfig",
    "Coordinates",
    "FileInput",
    "FileUploadError",
    "FileValidationError",
    "HTTPError",
    "LogLevel",
    "Model",
    "Perplexity",
    "PerplexityError",
    "RateLimitError",
    "ResearchClarifyingQuestionsError",
    "Response",
    "ResponseParsingError",
    "SearchFocus",
    "SearchResultItem",
    "SourceFocus",
    "StreamingError",
    "TimeRange",
]
