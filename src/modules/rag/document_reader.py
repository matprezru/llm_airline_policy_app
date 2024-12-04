# Standard imports
import logging
import os
from abc import ABC, abstractmethod
from typing import List, Optional, Union

# Third party imports
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class DocumentReader:
    """Class for reading documents from a file or directory path"""

    def __init__(self, data_paths: Union[List, str]) -> None:
        """Initialize DocumentReader class

        Args:
            data_path (str): path to file or directory to load.
                In case of directories, only the files in the root folder will be loaded.
                It also accepts a list of paths.
        """
        self.data_paths: List[str] = (
            data_paths if isinstance(data_paths, list) else [data_paths]
        )
        self.file_paths = self._get_files_list()

    def _get_files_list(self) -> List[str]:
        """Get list of documents to load.

        Returns:
            List[str]: list of absolute file paths
        """
        file_paths = []
        for path in self.data_paths:
            # If the path corresponds to a file, append it to the list
            if os.path.isfile(path):
                file_paths.append(os.path.abspath(path))
            # If the path corresponds to a directory, get all the internal files and append them to the list
            elif os.path.isdir(path):
                files = [
                    os.path.abspath(os.path.join(path, f))
                    for f in os.listdir(path)
                    if (os.path.isfile(os.path.join(path, f)) and not f.startswith("."))
                ]
                file_paths.extend(files)
            # If the path does not exist
            else:
                logger.warning("The provided path '{path}' does not exist")

        return file_paths

    def read_documents(self) -> List[List[Document]]:
        """Read list of documents in different formats, using the appropriate Loader.

        Returns:
            List[List[Document]]: each sublist corresponds to a file. Each element inside a sublist corresponds to a page.
        """
        documents = []

        for file_path in self.file_paths:

            logger.debug(f"Reading file {file_path}")
            loader = None

            # Get file extension
            _, ext = os.path.splitext(file_path)

            # Select corresponding loader depending on file extension
            if ext == ".pdf":
                loader = PdfLoader()
            elif ext == ".md":
                loader = MdLoader()
            else:
                logger.warning(
                    f"Could not load file '{file_path}'. Unsupported file type: '{ext}'"
                )
                # raise ValueError(f"Could not load file '{file_path}'. Unsupported file type: '{ext}'")

            # Load file and append to list
            if loader:
                doc_content = loader.load_file(file_path=file_path)
                documents.append(doc_content)

        # Raise exception if no documents could be loaded
        if not documents:
            raise Exception("No files could be loaded from the provided paths")

        return documents


class Loader(ABC):
    """Abstract class for loading documents in specific formats"""

    @abstractmethod
    def load_file(self, file_path: str) -> List[Document]:
        pass

    def _add_metadata(
        self,
        doc: Document,
        extension: Optional[str] = None,
        file_path: Optional[str] = None,
    ):
        """Add metadata fields to a Document object.
        These are the fields added:
            - source: the original path of the file
            - parent_folder: the name of the parent directory containing the file (i.e., the name of the Airline)
            - extension: the file extension

        Returns:
            Document: the document with modified metadata field.
        """
        if file_path:
            if "source" not in doc.metadata.keys():
                doc.metadata["source"] = file_path
            doc.metadata["parent_folder"] = os.path.basename(os.path.dirname(file_path))
        if extension:
            doc.metadata["extension"] = extension

        return doc


class PdfLoader(Loader):
    """Class for loading PDF files in LangChain format"""

    def load_file(self, file_path: str) -> List[Document]:
        """Loads a PDF file and returns a list of parsed pages in LangChain's Document format.

        Args:
            file_path (str): input file path

        Returns:
            List[Document]: list of Document Objects. Each element corresponds to a page from the pdf file.
        """
        loader = PyPDFLoader(file_path)
        document_pages = loader.load()
        for i, page in enumerate(document_pages):
            document_pages[i] = self._add_metadata(
                doc=page, extension=".pdf", file_path=file_path
            )
        return document_pages


class MdLoader(Loader):
    """Class for loading Markdown files in LangChain format"""

    def load_file(self, file_path: str) -> List[Document]:
        """Loads a Markdown file and returns a list of parsed pages in LangChain's Document format.

        Args:
            file_path (str): input file path

        Returns:
            List[Document]: list of Document Objects.
        """
        # # Alternative: using Langchain's unstructuredMarkdownLoader
        # from langchain_community.document_loaders import UnstructuredMarkdownLoader
        # loader = UnstructuredMarkdownLoader(file_path)
        # document_content = loader.load()

        with open(file_path, "r") as f:
            file_content_raw = f.read()

        document_object = Document(
            page_content=file_content_raw,
            metadata={
                "source": file_path,
            },
        )

        # Add metadata fields
        document_object = self._add_metadata(
            doc=document_object, extension=".md", file_path=file_path
        )

        # Encapsulate in List for consistency
        return [document_object]
