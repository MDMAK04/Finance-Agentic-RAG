import pandas as pd
from core.state import AgentState
from core.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
import re

def data_agent(state: AgentState) -> dict:
    print("[Data Agent] Analyse des données...")
    
    df = state.get("dataframe")
    if df is None:
        return {"answer": "Erreur : Aucun fichier CSV trouvé.", "history": ["data_agent"]}
    
    question = state["question"]
    
    # On donne au LLM les colonnes du CSV pour qu'il génère le bon code
    columns_info = ", ".join([f"{col} ({df[col].dtype})" for col in df.columns])
    
    prompt = f"""
    Tu es un expert Python et Data Analyst.
    Voici les colonnes du DataFrame disponible : {columns_info}
    
    Génère UNIQUEMENT du code Python (utilisant pandas) pour répondre à la question.
    Le DataFrame s'appelle 'df'. Ne mets pas de ```python, juste le code brut.
    Ne fais pas de print(), stocke le résultat final dans une variable 'resultat'.
    
    Question : {question}
    """
    
    messages = [
        SystemMessage(content="Tu génères uniquement du code Python exécutable."),
        HumanMessage(content=prompt)
    ]
    
    # 1. Le LLM génère le code
    llm = get_llm()
    response = llm.invoke(messages)
    code = response.content.strip()
    
    # Nettoyage du code (au cas où le LLM met des balises Markdown)
    code = re.sub(r'^```python\n|```$', '', code, flags=re.MULTILINE)
    
    print(f"Code généré :\n{code}\n")
    
    # 2. Exécution du code (Attention: exec est risqué, on ajoutera E2B plus tard)
    local_vars = {"df": df, "pd": pd}
    try:
        exec(code, {}, local_vars)
        resultat = local_vars.get("resultat", "Aucun résultat retourné.")
    except Exception as e:
        resultat = f"Erreur lors de l'exécution du code : {str(e)}"
        
    print("[Data Agent] Analyse terminée.")
    
    return {
        "answer": f"Résultat de l'analyse :\n{resultat}",
        "code": code,
        "result": resultat,
        "history": ["data_agent"]
    }