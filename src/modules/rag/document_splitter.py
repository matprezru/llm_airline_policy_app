# Standard imports
import logging
import os
from abc import ABC, abstractmethod
from typing import List

# Third party imports
from langchain_core.documents import Document
from langchain_text_splitters import (MarkdownHeaderTextSplitter,
                                      RecursiveCharacterTextSplitter)

logger = logging.getLogger(__name__)


class DocumentSplitter:
    """Class for splitting a list of documents into chunks"""

    def __init__(self, documents: List[List[Document]]) -> None:
        self.documents = documents

    def split_documents(self) -> List[List[Document]]:
        """Splits a list of documents into chunks, using the appropriate Splitter depending on the file type.

        Returns:
            List[List[Document]]: each sublist corresponds to a file. Each element inside a sublist corresponds to a chunk.
        """
        splitted_documents = []

        for doc in self.documents:

            logger.debug(f"Splitting document {doc[0].metadata.get('source')}")

            splitter = None

            ext = doc[0].metadata.get("extension", "")

            if ext == ".pdf":
                chunk_size = int(os.getenv("RECURSIVE_CHUNK_SIZE", 1200))
                chunk_overlap = int(os.getenv("RECURSIVE_CHUNK_OVERLAP", 80))
                splitter = RecursiveSplitter(
                    chunk_size=chunk_size, chunk_overlap=chunk_overlap
                )
            elif ext == ".md":
                splitter = MarkdownSplitter()
            else:
                logger.warning(
                    f"Could not split document '{doc[0].metadata.get('source')}'. Unsupported file type: '{ext}'"
                )

            # Split file and append to list
            if splitter:
                chunks = splitter.split_document(documents=doc)
                splitted_documents.append(chunks)

            # Raise exception if no documents could be loaded
        if not splitted_documents:
            raise Exception(
                "The specified documents could not be splitted into chunks."
            )

        return splitted_documents


class Splitter(ABC):
    """
    Abstract class for splitting a document using a specific method
    """

    @abstractmethod
    def split_document(self, documents: List[Document]) -> List[Document]:
        """
        Abstract method to split a document into chunks.

        Args:
            documents (List[Document]): document to be splitted. Each element of the list is a page of the document.

        Returns:
            List[Document]: list of chunks
        """
        pass


class RecursiveSplitter(Splitter):
    """Class for splitting documents into chunks using recursive chunking.

    This chunking method is based on dividing the text hierarchically and iteratively,
    using a set of separators (e.g: '\\n\\n', '\\n', ' '...).
    """

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        super().__init__()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )

    def split_document(self, documents: List[Document]) -> List[Document]:
        chunks = self.splitter.split_documents(documents)
        # Add chunk order in metadata (to create chunk ids later)
        for i, chunk in enumerate(chunks):
            chunk.metadata["order"] = i
        return chunks


class MarkdownSplitter(Splitter):
    """Class for splitting Markdown documents into chunks.

    This chunking method is based on creating chunks within specific header groups, taking
    advantage of the structure of the markdown file.
    """

    def __init__(self) -> None:
        super().__init__()

        # Set of headers we want to consider for splitting
        self.headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        # Use langchain's markdown splitter
        self.splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.headers_to_split_on
        )

    def split_document(self, documents: List[Document]) -> List[Document]:
        chunks = []
        for doc in documents:
            # Split document's text into chunks. The metadata of each chunk will include the headers it belongs to.
            splitted_doc = self.splitter.split_text(doc.page_content)
            for i, chunk in enumerate(splitted_doc):
                # Add markdown headers at the beginning of the chunk's content
                for header_symbol, header_name in reversed(self.headers_to_split_on):
                    header_content = chunk.metadata.get(header_name, "")
                    if header_content:
                        chunk.page_content = (
                            f"{header_symbol} {header_content}\n\n{chunk.page_content}"
                        )
                # Update chunk's metadata with corresponding document's metadata
                # chunk.metadata.update(doc.metadata)
                chunk.metadata = doc.metadata.copy()
                # Add chunk order in metadata (to create chunk ids later)
                chunk.metadata["order"] = i
                # Append chunk to final list
                chunks.append(chunk)
        return chunks
