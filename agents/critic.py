from core.state import AgentState

def critic(state: AgentState) -> dict:
    print("[Critic] Vérification de la réponse...")
    
    answer = state.get("answer", "")
    
    if not answer or len(answer.strip()) < 5:
        print("[Critic] La réponse est vide ou trop courte.")
        return {"critique": "RETRY"}
    
    print("[Critic] La réponse semble correcte.")
    return {"critique": "OK"}