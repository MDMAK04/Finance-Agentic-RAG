from core.state import AgentState
from core.llm import get_llm
from core.vector_store import get_vector_store
from langchain_core.messages import HumanMessage, SystemMessage

def rag_agent(state: AgentState) -> dict:

    print("[RAG Agent] Recherche dans les documents...")
    
    question = state["question"]
    
    # 1. Se connecter à Qdrant
    vector_store = get_vector_store()
    
    # 2. Chercher les 5 passages les plus pertinents
    docs = vector_store.similarity_search(question, k=5)
    
    # 3. Construire le contexte à partir des documents trouvés
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # 4. Créer le prompt (on demande au LLM d'utiliser UNIQUEMENT le contexte)
    messages = [
        SystemMessage(content=(
            "Tu es un analyste financier. Réponds à la question en utilisant UNIQUEMENT "
            "les informations du contexte fourni ci-dessous. Si la réponse n'est pas "
            "dans le contexte, dis 'Je ne trouve pas cette information dans les documents.'"
        )),
        HumanMessage(content=f"Contexte:\n{context}\n\nQuestion: {question}")
    ]
    
    # 5. Appeler le LLM
    llm = get_llm()
    response = llm.invoke(messages)
    
    print("[RAG Agent] Réponse générée avec succès.")
    
    return {
        "answer": response.content,
        "documents": docs,
        "history": ["rag_agent"]
    }