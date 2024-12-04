"""
Module containing the API Endpoints for asking queries to the RAG system.

The path of all these endpoints starts with "/query"
"""

from typing import List
import logging
import os

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.modules.rag.chat_memory import ChatMemory
from src.services.query_service import query_rag


logger = logging.getLogger(__name__)

# Define router
router = APIRouter()

# Initialize custom object to store Chat Memory and make it persistent between queries
chat_memory = ChatMemory(max_memory=int(os.getenv("MAX_CHAT_MEMORY", 3)))
def get_chat_memory():
    return chat_memory


# Define a request body model (if needed)
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    
# Endpoint for asking queries
@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, chat_memory: ChatMemory = Depends(get_chat_memory)):
    
    query = request.query
    logger.info(f"User query received: '{query}'")
    
    current_memory = chat_memory.get_memory()
    
    # Ask RAG
    response = query_rag(query_text=query, memory=current_memory)
    
    # Separate response and sources
    answer = response.get('answer')
    sources = response.get('sources')
    
    logger.info(f"Answer generated:\n{answer}")
    
    # Update memory
    chat_memory.add_memory(query, answer)
    
    return ChatResponse(answer=answer, sources=sources)