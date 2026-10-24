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
    # On liste les colonnes très clairement
    columns_list = ", ".join(df.columns)
    
    # --- ÉTAPE 1 : Génération et exécution du code ---
    prompt_code = f"""
    Tu es un expert Python et Data Analyst.
    Voici les SEULES colonnes autorisées dans le DataFrame : {columns_list}
    
    Génère UNIQUEMENT du code Python pour répondre à la question.
    - Le DataFrame s'appelle 'df'.
    - SI ET SEULEMENT SI la question demande un graphique, utilise 'px' (plotly.express) et stocke la figure dans 'fig'.
    - IMPORTANT : Utilise EXCLUSIVEMENT les colonnes listées ci-dessus. N'invente aucun nom de colonne.
    - SINON, stocke le résultat dans 'resultat'.
    - Ne mets pas de print(), pas de balises Markdown.
    
    Question : {question}
    """
    
    llm = get_llm()
    response = llm.invoke([
        SystemMessage(content="Tu génères uniquement du code Python exécutable."),
        HumanMessage(content=prompt_code)
    ])
    code = re.sub(r'^```python\n|```$', '', response.content.strip(), flags=re.MULTILINE)
    
    # --- ÉTAPE 2 : Exécution du code ---
    local_vars = {"df": df, "pd": pd, "px": px, "go": go}
    try:
        exec(code, {}, local_vars)
        resultat = local_vars.get("resultat", None)
        fig = local_vars.get("fig", None)
    except Exception as e:
        print(f"Erreur d'exécution : {e}")
        return {"answer": f"L'analyse a échoué car l'IA a généré un code invalide. Détail : {str(e)}", "history": ["data_agent"]}
        
    # --- ÉTAPE 3 : Formulation de la réponse ---
    if fig is not None:
        # Pour le graphique, on demande une analyse de la tendance
        prompt_texte = f"""
        L'utilisateur a demandé : {question}
        Un graphique a été généré avec succès.
        
        Rédige une réponse professionnelle en 2 parties :
        1. Une phrase d'introduction : "Voici le graphique illustrant...".
        2. Un paragraphe d'analyse : Décris ce que ce graphique montre (tendances, comparaisons, points hauts/bas).
        """
    else:
        # Pour un tableau ou un chiffre, on formate proprement
        if isinstance(resultat, pd.Series):
            resultat_md = resultat.to_frame().to_markdown()
        elif isinstance(resultat, pd.DataFrame):
            resultat_md = resultat.to_markdown()
        else:
            resultat_md = str(resultat)
            
        prompt_texte = f"""
        L'utilisateur a demandé : {question}
        Voici le résultat de l'analyse : 
        {resultat_md}
        
        Rédige une phrase d'introduction claire, puis affiche le tableau Markdown.
        """
    
    reponse_llm = llm.invoke([
        SystemMessage(content="Tu es un analyste financier expert. Tes analyses sont précises et professionnelles."),
        HumanMessage(content=prompt_texte)
    ])
    
    answer_final = reponse_llm.content
    figures_list = [fig] if fig is not None else []
    
    return {
        "answer": answer_final,
        "code": code,
        "result": str(resultat),
        "figures": figures_list,
        "history": ["data_agent"]
    }