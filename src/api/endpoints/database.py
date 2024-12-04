"""
Module containing the API Endpoints related to database operations: upload documents, list chunks, retrieve chunks...

The path of all these endpoints starts with "/database"
"""

import logging
import os
from typing import Dict, List, Union

from fastapi import APIRouter
from pydantic import BaseModel

from src.modules.rag.vector_db import VectorDB
from src.services.database_service import load_documents

logger = logging.getLogger(__name__)

# Define router
router = APIRouter()


# Define request/response models
class UploadDocRequest(BaseModel):
    data_path: Union[str, List[str]]


class RetrieveChunkRequest(BaseModel):
    id: str


class RetrieveChunkResponse(BaseModel):
    page_content: str
    metadata: Dict


# Endpoint for loading documents to vector database
@router.post("/upload_documents")
async def upload_and_index_document(request: UploadDocRequest):
    data_path = request.data_path
    logger.info(f"Received request to upload the following documents: {data_path}")
    message = load_documents(data_path=data_path)
    return message


# Endpoint for getting list of IDs of indexed elements
@router.get("/list_indexed_items")
async def get_indexed_items():
    chroma_path = os.getenv("CHROMA_PATH")
    vector_db = VectorDB(persist_dir=chroma_path)
    existing_ids = vector_db.list_indexed_elements()
    logger.info(f"There are {len(existing_ids)} elements indexed in the vector DB")
    return {"n_items": len(existing_ids), "ids": existing_ids}


# Endpoint for retrieving a chunk and its metadata from the Vector DB
@router.post("/retrieve_chunk", response_model=RetrieveChunkResponse)
async def retrieve_chunk(request: RetrieveChunkRequest):
    chroma_path = os.getenv("CHROMA_PATH")
    vector_db = VectorDB(persist_dir=chroma_path)
    chunk = vector_db.get_by_id(id=request.id)
    return RetrieveChunkResponse(
        page_content=chunk.get("page_content", ""), metadata=chunk.get("metadata", {})
    )


# Endpoint for clearing the Vector DB
@router.delete("/clear_database")
async def clear_database():
    chroma_path = os.getenv("CHROMA_PATH")
    vector_db = VectorDB(persist_dir=chroma_path)
    vector_db.clear_database()
    return "The vector database has been deleted"
