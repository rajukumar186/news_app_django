import os
from google import genai
from google.genai import errors
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from django.core.cache import cache
# Load once globally
load_dotenv()
_embed_model = None
_chroma_client = None
_collection = None

def get_rag_components():
    global _embed_model, _chroma_client, _collection
    if _embed_model is None:
        print("Loading local embedding model for WebSocket RAG...")
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    if _chroma_client is None:
        _chroma_client = chromadb.Client()
        _collection = _chroma_client.get_or_create_collection(name="news_knowledge_base")
    return _embed_model, _collection

def ingest_combined_news_to_rag(combined_news_list):
    """
    Takes the combined news list from newsapp and syncs them into ChromaDB.
    """
    if not combined_news_list:
        return False

    embed_model, collection = get_rag_components()

    for i, item in enumerate(combined_news_list):
        doc_id = f"news_{item.get('section_type', 'general')}_{i}"
        title = item.get('title', '')
        description = item.get('description', '') or item.get('content', '')
        text = f"{title}\n\n{description}"
        
        chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
        if not chunks:
            continue
            
        embeddings = embed_model.encode(chunks).tolist()
        ids = [f"{doc_id}_chunk_{j}" for j in range(len(chunks))]
        
        collection.upsert(
            documents=chunks,
            embeddings=embeddings,
            ids=ids
        )
    print(f"✅ Successfully synced {len(combined_news_list)} articles into chat RAG knowledge base.")
    return True

def query_rag_assistant(user_question: str) -> str:
    embed_model, collection = get_rag_components()
    query_vector = embed_model.encode([user_question]).tolist()
    
    results = collection.query(
        query_embeddings=query_vector,
        n_results=3
    )
    
    retrieved_chunks = results["documents"][0] if results["documents"] and results["documents"][0] else []
    context_str = "\n\n".join(retrieved_chunks) if retrieved_chunks else "No relevant context found."
    
    prompt = f"""You are a helpful AI news assistant for The People's Era. Answer the user question using ONLY the provided context. If the answer cannot be found in the context, state that you don't have enough recent information.

Context:
{context_str}

User Question: {user_question}
"""
    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",  # Update to a valid supported model identifier if needed
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"❌ Error generating response: {e}"

def query_django_rag(user_question: str) -> str:
    return query_rag_assistant(user_question)