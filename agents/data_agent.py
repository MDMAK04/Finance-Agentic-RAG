import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from core.state import AgentState
from core.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

def data_agent(state: AgentState) -> dict:

    print("[Data Agent] Analyse des données...")
    
    df = state.get("dataframe")
    if df is None:
        return {"answer": "Erreur : Aucun fichier CSV trouvé.", "history": ["data_agent"]}
    
    question = state["question"]
    columns_info = ", ".join([f"{col} ({df[col].dtype})" for col in df.columns])
    
    prompt = f"""
    Tu es un expert Python, Data Analyst et expert Plotly.
    Voici les colonnes du DataFrame : {columns_info}
    
    Génère UNIQUEMENT du code Python pour répondre à la question.
    - Le DataFrame s'appelle 'df'.
    - Si la question demande un graphique, utilise 'px' (plotly.express) ou 'go' (plotly.graph_objects) et stocke la figure dans une variable 'fig'.
    - Si c'est juste un calcul, stocke le résultat dans une variable 'resultat'.
    - Ne mets pas de print().
    - Ne mets pas de balises Markdown (```python), juste le code brut.
    
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
    
    # Nettoyage du code
    code = re.sub(r'^```python\n|```$', '', code, flags=re.MULTILINE)
    
    print(f"Code généré :\n{code}\n")
    
    # 2. Exécution du code
    local_vars = {"df": df, "pd": pd, "px": px, "go": go}
    try:
        exec(code, {}, local_vars)
        resultat = local_vars.get("resultat", "Aucun résultat texte.")
        fig = local_vars.get("fig", None)
    except Exception as e:
        resultat = f"Erreur lors de l'exécution du code : {str(e)}"
        fig = None
        
    print("[Data Agent] Analyse terminée.")
    
    # 3. On prépare la réponse
    figures_list = [fig] if fig else []
    
    return {
        "answer": f"Résultat de l'analyse :\n{resultat}",
        "code": code,
        "result": resultat,
        "figures": figures_list,
        "history": ["data_agent"]
    }