from typing import TypedDict, Annotated, Any
from operator import add

class AgentState(TypedDict):
    question: str
    files: list
    
    # 2. Routage (géré par le Supervisor)
    route: str
    retry_count: int
    
    # 3. Données RAG (géré par le RAG Agent)
    documents: list
    
    # 4. Données Tabulaire (géré par le Data Agent)
    dataframe: Any
    code: str
    result: Any
    figures: list
    
    # 5. Sortie (géré par Critic/Synthesizer)
    answer: str
    critique: str
    
    # 6. Historique (s'accumule au fil des étapes)
    history: Annotated[list, add]
