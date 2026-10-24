from langgraph.graph import StateGraph, START, END
from core.state import AgentState
from core.routing_rules import check_quality

from agents.supervisor import supervisor
from agents.rag_agent import rag_agent
from agents.data_agent import data_agent
from agents.general_agent import general_agent
from agents.synthesizer import synthesizer
from agents.critic import critic

def build_graph():
    
    # 1. Initialiser le graphe avec notre State
    workflow = StateGraph(AgentState)
    
    # 2. Ajouter les nœuds (les agents)
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("rag_agent", rag_agent)
    workflow.add_node("data_agent", data_agent)
    workflow.add_node("general_agent", general_agent)
    workflow.add_node("synthesizer", synthesizer)
    workflow.add_node("critic", critic)
    
    # 3. Définir le point d'entrée
    workflow.add_edge(START, "supervisor")
    
    # 4. Le Supervisor route vers le bon agent
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["route"], # On lit la clé 'route'
        {
            "rag": "rag_agent",
            "data": "data_agent",
            "general": "general_agent"
        }
    )
    
    # 5. Tous les agents vont au Synthesizer
    workflow.add_edge("rag_agent", "synthesizer")
    workflow.add_edge("data_agent", "synthesizer")
    workflow.add_edge("general_agent", "synthesizer")
    
    # 6. Le Synthesizer va au Critic
    workflow.add_edge("synthesizer", "critic")
    
    # 7. Le Critic décide si on s'arrête ou si on réessaie
    workflow.add_conditional_edges(
        "critic",
        check_quality,
        {
            "end": END,
            "retry": "supervisor" # Si ça échoue, on renvoie au début
        }
    )
    
    return workflow.compile()

# On crée l'application finale
app = build_graph()