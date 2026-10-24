from core.state import AgentState

def synthesizer(state: AgentState) -> dict:
    """Assemble la réponse finale."""
    print("[Synthesizer] Assemblage de la réponse finale...")
    # Pour l'instant, on garde juste la réponse de l'agent
    return {"history": ["synthesizer"]}