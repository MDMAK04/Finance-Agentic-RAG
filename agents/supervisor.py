from core.state import AgentState
from core.routing_rules import route_query

def supervisor(state: AgentState) -> dict:

    print("[Supervisor] Analyse de la requête...")
    
    route = route_query(state)
    
    print(f"[Supervisor] Décision : Envoyer vers l'agent '{route}'")
    
    return {
        "route": route,
        "history": ["supervisor"]
    }