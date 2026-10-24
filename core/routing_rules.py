import os

def route_query(state: dict) -> str:
    files = state.get("files", [])
    
    for f in files:
        if f.endswith(('.csv', '.xlsx', '.xls')):
            return "data"
            
    for f in files:
        if f.endswith('.pdf'):
            return "rag"
            
    return "general"

def check_quality(state: dict) -> str:
    """
    Vérifie si le critique a validé la réponse.
    Si c'est bon, on termine. Sinon, on réessaie (jusqu'à 2 fois).
    """
    critique = state.get("critique", "")
    retry_count = state.get("retry_count", 0)
    
    if "OK" in critique or retry_count >= 2:
        return "end"
    else:
        return "retry"