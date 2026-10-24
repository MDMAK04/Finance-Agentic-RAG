import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from langchain_qdrant import QdrantVectorStore 
from core.llm import get_embeddings

COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "finance_docs")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

def get_qdrant_client() -> QdrantClient:
    return QdrantClient(url=QDRANT_URL)

def init_collection(client: QdrantClient):
    """
    Crée la collection si elle n'existe pas.
    On utilise une dimension de 768 car c'est la taille des vecteurs de nomic-embed-text.
    """
    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if not exists:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
        print(f"Collection '{COLLECTION_NAME}' créée.")
    else:
        print(f"ℹ️ Collection '{COLLECTION_NAME}' existe déjà.")

def get_vector_store() -> QdrantVectorStore:
    """
    Retourne l'objet QdrantVectorStore de LangChain.
    C'est lui qui fera le lien entre le texte et Qdrant.
    """
    client = get_qdrant_client()
    init_collection(client)
    
    embeddings = get_embeddings()
    
    return QdrantVectorStore(
        client=client,
        collection_name=COLLECTION_NAME,
        embedding=embeddings,
    )

def index_documents(chunks: list):
    """
    Prend une liste de chunks (documents) et les stocke dans Qdrant.
    """
    if not chunks:
        print("Aucun document à indexer.")
        return
        
    print(f"Indexation de {len(chunks)} chunks dans Qdrant...")
    vector_store = get_vector_store()
    
    # Ajout des documents (LangChain gère les embeddings automatiquement)
    vector_store.add_documents(chunks)
    print("Indexation terminée !")