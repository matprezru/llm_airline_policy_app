import os
from typing import List, Union
import logging

from src.modules.rag.document_reader import DocumentReader
from src.modules.rag.document_splitter import DocumentSplitter
from src.modules.rag.vector_db import VectorDB


logger = logging.getLogger(__name__)

def load_documents(data_path: Union[List, str]) -> str:
    """Function to load a document, directory or list of documents into the vector database.
    The loading process is divided in three steps:
    1. Reading the files
    2. Splitting the documents into chunks
    3. Indexing the chunks in the vector database

    Args:
        data_path (Union[List, str]): path to file or directory to load.
                In case of directories, only the files in the root folder will be loaded.
                It also accepts a list of paths.

    Returns:
        str: message indicating success or error.
    """
    try:
        
        # 1. Read documents
        logger.info("Reading documents.")
        document_reader = DocumentReader(data_path)
        documents = document_reader.read_documents()
        logger.info(f"{len(documents)} documents have been read.")

        # 2. Split documents into chunks
        logger.info("Splitting documents into chunks.")
        document_splitter = DocumentSplitter(documents = documents)
        chunks = document_splitter.split_documents()
        
        # 3. Index chunks in vector database
        logger.info("Indexing documents in vector database.")
        chroma_path = os.getenv("CHROMA_PATH")
        vector_db = VectorDB(persist_dir=chroma_path)
        message = vector_db.index_documents(documents=chunks)

        return message
    
    except Exception as e:
        return f"Error. Exception occurred during upload process: '{e}'"
