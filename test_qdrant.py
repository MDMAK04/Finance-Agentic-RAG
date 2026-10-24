from core.ingestion import load_pdf
from core.vector_store import index_documents, get_vector_store

# 1. On charge le PDF de test
print("📄 Chargement du PDF...")
chunks = load_pdf("data/documents/test.pdf")

# 2. On les envoie dans Qdrant
index_documents(chunks)

# 3. On teste la recherche
print("\n🔍 Test de recherche...")
vector_store = get_vector_store()
results = vector_store.similarity_search("Quels sont les facteurs de risque cardiovasculaire ?", k=2)

for i, doc in enumerate(results):
    print(f"\n--- Résultat {i+1} (Page {doc.metadata.get('page', '?')}) ---")
    print(doc.page_content[:300] + "...")
