import os
from typing import Dict, List, Optional
import logging

from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.modules.rag.embeddings import CustomEmbeddings
from src.modules.rag.prompts import DEFAULT_PROMPT_TEMPLATE


logger = logging.getLogger(__name__)


def query_rag(query_text: str, memory: List[Optional[Dict]] = []) -> dict:
    """Main function to make a query to the RAG system and generate an answer using an LLM.

    Args:
        query_text (str): query
        memory (List[Optional[Dict]]): chat memory, given as a list of dictionaries (fields "question", "answer"). Optional.

    Returns:
        dict: dictionary containing the fields "answer" and "sources"
    """
    
    # Prepare the DB.
    embeddings = CustomEmbeddings(provider = os.getenv("EMBEDDINGS_PROVIDER"), model_name = os.getenv("EMBEDDINGS_MODEL"))
    chroma_path = os.getenv("CHROMA_PATH")
    db = Chroma(
        persist_directory=chroma_path, 
        embedding_function=embeddings.get_embedding_function()
        )

    filter_by_airline=os.getenv("FILTER_BY_AIRLINE", "False").lower() == "true"
    metadata_filter = None
    if filter_by_airline:

        # Get list of available airlines in the db (different "parent_folder" field in metadata)
        metadata_list = db.get(include=["metadatas"]).get("metadatas")
        airlines_available = set([metadata.get("parent_folder", "") for metadata in metadata_list])

        # Check if any specific airline is mentioned in the query (
        # TODO: This is a Naive Approach. Improvements: use and LLM, NER or Fuzzy Matching to recognize the airline(s) the query refers to.
        airlines_mentioned = []
        for airline in airlines_available:
            if airline.replace(" ", "").lower() in query_text.replace(" ", "").lower():
                airlines_mentioned.append(airline)

        logger.debug(f"The query has been identified to refer to the following airlines: {airlines_mentioned}. Retrieved sources will be filtered to include only documents from these airlines.")
        
        # Set up filters for the mentioned airline(s)
        if airlines_mentioned:
            metadata_filter = {"parent_folder": {"$in": airlines_mentioned}}

    # Search relevant documents in the database
    results = db.similarity_search_with_score(
        query_text, 
        k=int(os.getenv("TOP_K", 3)), 
        filter=metadata_filter
    )

    # Compose context from retrieved sources
    context_text = "\n\n---\n\n".join([
        f"### Source {i+1}:\n{doc.page_content}"
        for i, (doc, _score) in enumerate(results)
    ])
    
    # Compose memory context
    if memory:
        memory_text = "\n".join([f"- **Q:** {qa['question']}\n  **A:** {qa['answer']}" for qa in memory])
    else:
        memory_text = "No previous interactions available."
        
    # Format the prompt
    prompt_template = ChatPromptTemplate.from_template(DEFAULT_PROMPT_TEMPLATE)
    prompt = prompt_template.format(
        memory=memory_text, 
        context=context_text, 
        question=query_text
    )
    
    # Get LLM response
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
    )
    
    response_text = llm.invoke(prompt).content

    # Return answer and sources
    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    
    response = {'answer': response_text, 'sources': sources}
    
    return response