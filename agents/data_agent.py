import pandas as pd
import re
from core.state import AgentState
from core.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage
from core.sandbox.local_sandbox import run_code_safely

def data_agent(state: AgentState) -> dict:
    print("[Data Agent] Analyse des données...")
    
    df = state.get("dataframe")
    if df is None:
        return {"answer": "Erreur : Aucun fichier CSV trouvé.", "history": ["data_agent"]}
    
    question = state["question"]
    columns_list = ", ".join(df.columns)
    
    prompt_code = f"""
    Tu es un expert Python et Data Analyst.
    Voici les SEULES colonnes autorisées dans le DataFrame : {columns_list}
    
    Génère UNIQUEMENT du code Python pour répondre à la question.
    - Le DataFrame s'appelle 'df'.
    - SI ET SEULEMENT SI la question demande un graphique, utilise 'px' (plotly.express) et stocke la figure dans 'fig'.
    - IMPORTANT : Si tu génères un graphique, stocke AUSSI les données agrégées dans la variable 'resultat' (ex: df.groupby('region').sum()) pour que l'analyse textuelle soit correcte.
    - Utilise EXCLUSIVEMENT les colonnes listées ci-dessus. N'invente aucun nom de colonne.
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
    
    # --- EXÉCUTION SÉCURISÉE ---
    resultat, fig, error_msg = run_code_safely(code, df)
    
    if error_msg:
        print(f"Erreur bloquée par la Sandbox : {error_msg}")
        return {"answer": f"L'analyse a échoué (Sandbox) : {error_msg}", "history": ["data_agent"]}
        
    # --- ÉTAPE 3 : Formulation de la réponse ---
    if fig is not None:
        # On prépare les vraies données pour que le LLM analyse correctement
        if isinstance(resultat, pd.Series):
            data_to_analyze = resultat.to_frame().to_markdown()
        elif isinstance(resultat, pd.DataFrame):
            data_to_analyze = resultat.to_markdown()
        else:
            # Si l'IA n'a pas mis dans resultat, on lui donne un aperçu du dataframe
            data_to_analyze = df.head(10).to_markdown()

        prompt_texte = f"""
        L'utilisateur a demandé : {question}
        Un graphique a été généré pour répondre à cette question.
        Voici les VRAIES données qui ont servi à générer ce graphique :
        {data_to_analyze}
        
        Rédige UN SEUL paragraphe d'analyse professionnelle (sans titre, sans numéro, sans liste à puces).
        Commence directement par une phrase d'introduction fluide (ex: "L'analyse des données révèle que...") 
        puis enchaîne immédiatement sur l'analyse des tendances, des comparaisons et des points remarquables.
        Base-toi UNIQUEMENT sur les données fournies ci-dessus. Ne devine pas les noms.
        """
    else:
        if isinstance(resultat, pd.Series):
            resultat_md = resultat.to_frame().to_markdown()
        elif isinstance(resultat, pd.DataFrame):
            resultat_md = resultat.to_markdown()
        else:
            resultat_md = str(resultat)
            
        prompt_texte = f"""
        L'utilisateur a demandé : {question}
        Voici le résultat : {resultat_md}
        Rédige une phrase d'introduction claire, puis affiche le tableau Markdown.
        """
    
    reponse_llm = llm.invoke([
        SystemMessage(content="Tu es un analyste financier expert."),
        HumanMessage(content=prompt_texte)
    ])
    
    return {
        "answer": reponse_llm.content,
        "code": code,
        "result": str(resultat),
        "figures": [fig] if fig is not None else [],
        "history": ["data_agent"]
    }