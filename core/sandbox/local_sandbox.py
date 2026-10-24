import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import contextlib

def run_code_safely(code: str, df: pd.DataFrame):
    """
    Exécute le code Python généré par le LLM de manière isolée.
    (Pour l'instant, on utilise une isolation par variables locales et capture de stdout,
    mais on bloquera les imports dangereux).
    """
    # 1. Créer un environnement isolé
    local_vars = {"df": df.copy(), "pd": pd, "px": px, "go": go}
    
    # 2. Bloquer les imports dangereux (sécurité de base)
    forbidden_keywords = ["import os", "import sys", "import subprocess", "open(", "__import__", "eval(", "exec("]
    for keyword in forbidden_keywords:
        if keyword in code:
            raise ValueError(f"Sécurité : Le code généré contient une instruction interdite ({keyword}).")
            
    # 3. Capturer la sortie standard (si l'IA fait un print par erreur)
    output_buffer = io.StringIO()
    
    try:
        with contextlib.redirect_stdout(output_buffer):
            # Exécution du code
            exec(code, {}, local_vars)
            
        resultat = local_vars.get("resultat", None)
        fig = local_vars.get("fig", None)
        
        return resultat, fig, None
        
    except Exception as e:
        return None, None, str(e)
    