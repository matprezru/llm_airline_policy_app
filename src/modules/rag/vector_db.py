import logging
import os
import shutil
from typing import Dict, List, Optional, Union

from langchain.schema.document import Document
from langchain_chroma import Chroma

from src.modules.rag.embeddings import CustomEmbeddings

logger = logging.getLogger(__name__)


class VectorDB:
    """Custom class for interacting with the Chroma Vector DB"""

    def __init__(self, persist_dir: str) -> None:

        self.persist_dir = persist_dir
        self.embeddings = CustomEmbeddings(
            provider=os.getenv("EMBEDDINGS_PROVIDER"),
            model_name=os.getenv("EMBEDDINGS_MODEL"),
        )
        self.db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings.get_embedding_function(),
        )

    def index_documents(self, documents: List[List[Document]]) -> str:
        """Index a list of document chunks in the vector database

        Args:
            documents (List[List[Document]]): list of documents. Each document is a sublist composed by multiple chunks.

        Returns:
            str: message indicating success or error.
        """

        # Flatten list of chunks
        chunks = [chunk for doc in documents for chunk in doc]

        logger.info(
            f"There are {len(documents)} documents to be indexed in the vector database."
        )
        logger.info(
            f"There are {len(chunks)} chunks to be indexed in the vector database."
        )

        # Calculate Page IDs.
        chunks = self._assign_chunk_ids(chunks=chunks)

        # Add or Update the documents.
        existing_items = self.db.get(include=[])  # IDs are always included by default
        existing_ids = set(existing_items["ids"])
        logger.debug(f"Number of existing items in DB: {len(existing_ids)}")

        # Only add chunks that don't exist in the DB
        new_chunks = [
            chunk for chunk in chunks if chunk.metadata["id"] not in existing_ids
        ]
        if new_chunks:
            logger.info(f"Adding {len(new_chunks)} new items to the vector database.")
            new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
            uploaded_ids = self.db.add_documents(
                documents=new_chunks, ids=new_chunk_ids
            )
            if uploaded_ids:
                message = f"{len(uploaded_ids)}/{len(new_chunks)} chunks have been uploaded successfully"
                logger.info(message)
            else:
                raise Exception(
                    "The documents could not be indexed in the vector database."
                )
        else:
            message = "There are no new chunks to add to the vector database."
            logger.info(message)

        return message

    def list_indexed_elements(self) -> List[str]:
        """Returns the list of IDs of the elements indexed in the Vector DB.

        Returns:
            List[str]: list of IDs
        """
        # Retrieve List of chunk IDs
        existing_items = self.db.get(include=[])  # IDs are always included by default

        # Convert into a set to avoid duplicates
        existing_ids = set(existing_items["ids"])

        return existing_ids

    def get_by_id(self, id: str) -> Optional[Dict]:
        """Retrieves an element from the vector DB, given its ID

        Args:
            id (str): id of the chunk to retrieve

        Returns:
            Optional[Dict]: dictionary containing "content" and "metadata" fields.
        """
        item = self.db.get(ids=id, include=["metadatas", "documents"])
        if item:
            content = item.get("documents", [])[0]
            metadata = item.get("metadatas", [])[0]
            return {"page_content": content, "metadata": metadata}
        else:
            return None

    def clear_database(self):
        """Deletes the Vector DB."""
        logger.info(f"Deleting vector database: '{self.persist_dir}'")
        if os.path.exists(self.persist_dir):
            shutil.rmtree(self.persist_dir)
        logger.info("The vector database has been deleted.")

    def delete_by_id(self, ids: Union[str, List[str]]):
        """Deletes items from the vector DB given their IDs.

        Args:
            ids (str | List[str]): ID(s) of the element(s) to be deleted.
        """
        if not isinstance(ids, List):
            ids = [ids]
        self.db.delete(ids=ids)
        logger.info(f"{len(ids)} items have been deleted from the vector database.")

    def _assign_chunk_ids(self, chunks: List[Document]) -> List[Document]:
        """Assign id to each chunk, in the metadata field "id".

        The format of the chunk id is: "parent_folder/filename:order"

        e.g.: "AmericanAirlines/Policy.md:5"

        Args:
            chunks (List[Document]): list of chunks, in Langchain's Document format.

        Returns:
            List[Document]: list of chunks with updated "id" field in their metadata.
        """
        for chunk in chunks:
            # Retrieve metadata that will be use to compose the chunk id
            parent_folder = chunk.metadata.get("parent_folder", "")
            source = chunk.metadata.get("source", "")
            order = chunk.metadata.get("order", "")

            # Get name of the file the chunk belongs to
            filename = os.path.basename(source)

            # Compose the chunk id
            # e.g.: "AmericanAirlines/Policy.md:5"
            chunk_id = f"{parent_folder}/{filename}:{order}"

            # Add id to chunk's metadata
            chunk.metadata["id"] = chunk_id

        return chunks
