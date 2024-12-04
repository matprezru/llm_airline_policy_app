import logging
from enum import Enum

from langchain.embeddings.base import Embeddings
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)


class EmbeddingProvider(str, Enum):
    """Available Embeddings Providers"""

    OPENAI = "openai"
    HUGGINGFACE_BGE = "huggingface_bge"


class CustomEmbeddings:
    """
    Wrapper class for using embeddings from different providers in Langchain.
    """

    def __init__(self, provider: str = "huggingface_bge", model_name: str = None):
        """Initialize the CustomEmbedding class.

        Args:
            provider (str): The provider of embeddings, e.g., "openai", "huggingface_bge". Defaults to "huggingface_bge".
            model_name (str): The model name for the embeddings. Defaults to None.
        """
        self.embeddings = self._load_embedding_model(provider, model_name)

    def _load_embedding_model(self, provider: str, model_name: str) -> Embeddings:
        """
        Load the appropriate embedding model based on the provider.

        Returns:
            An instance of a LangChain Embeddings object.
        """

        logger.debug(
            f"Loading embedding model. Provider: {provider}. Model name: {model_name}"
        )

        if provider == EmbeddingProvider.OPENAI:
            return OpenAIEmbeddings(model=model_name or "text-embedding-3-large")

        elif provider == EmbeddingProvider.HUGGINGFACE_BGE:
            return HuggingFaceBgeEmbeddings(
                model_name=model_name or "BAAI/bge-base-en-v1.5",
                model_kwargs={"device": "cpu"},
                encode_kwargs={
                    "normalize_embeddings": True
                },  # set True to compute cosine similarity
            )
        else:
            raise ValueError(
                f"Unsupported embedding provider: '{provider}'. Must be one of: {[e.value for e in EmbeddingProvider]}."
            )

    def get_embedding_function(self) -> Embeddings:
        """
        Returns the embedding function
        """
        return self.embeddings
