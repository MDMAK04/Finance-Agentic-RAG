from core.state import AgentState
from core.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

def general_agent(state: AgentState) -> dict:

    print("[General Agent] Réponse en cours...")
    
    llm = get_llm()
    
    messages = [
        SystemMessage(content="Tu es un assistant financier expert. Réponds de manière claire et concise."),
        HumanMessage(content=state["question"])
    ]
    
    response = llm.invoke(messages)
    
    return {
        "answer": response.content,
        "history": ["general_agent"]
    }