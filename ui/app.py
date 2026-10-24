import sys
import os
import asyncio

# Ajouter le dossier racine au chemin Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import chainlit as cl
from core.graph import app
from core.ingestion import load_pdf, load_csv
from core.vector_store import index_documents
import pandas as pd

@cl.on_chat_start
async def start():
    """S'exécute au début de chaque nouvelle conversation."""
    cl.user_session.set("state", {
        "question": "",
        "files": [],
        "dataframe": None,
        "retry_count": 0,
        "history": []
    })
    await cl.Message(
        content="Bienvenue sur **Finance-Agent** !\n\n"
                "Vous pouvez :\n"
                "- Poser une question générale sur la finance.\n"
                "- Uploader un **PDF** (rapport annuel) et poser une question dessus.\n"
                "- Uploader un **CSV/Excel** et demander une analyse de données.\n\n"
                "Comment puis-je vous aider aujourd'hui ?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    """S'exécute à chaque fois que l'utilisateur envoie un message."""
    
    # 1. Récupérer l'état actuel de la session
    state = cl.user_session.get("state")
    state["question"] = message.content
    state["retry_count"] = 0
    state["history"] = []
    
    # 2. Gérer les fichiers uploadés (s'il y en a)
    if message.elements:
        for element in message.elements:
            if element.name.endswith(".pdf"):
                msg = cl.Message(content=f"Lecture et indexation du PDF : {element.name}...")
                await msg.send()
                
                # On exécute l'indexation dans un thread séparé pour ne pas bloquer l'interface
                chunks = await cl.make_async(load_pdf)(element.path)
                await cl.make_async(index_documents)(chunks)
                
                state["files"].append(element.name)
                msg.content = f"PDF `{element.name}` indexé avec succès !"
                await msg.update()
                await asyncio.sleep(1) # Petite pause pour lire le message
                await msg.remove() # On nettoie le message
                
            elif element.name.endswith((".csv", ".xlsx", ".xls")):
                msg = cl.Message(content=f"Lecture du fichier : {element.name}...")
                await msg.send()
                
                df = await cl.make_async(load_csv)(element.path)
                state["dataframe"] = df
                
                state["files"].append(element.name)
                msg.content = f"Fichier `{element.name}` chargé en mémoire (Dimensions : {df.shape[0]} lignes, {df.shape[1]} colonnes)."
                await msg.update()
                await asyncio.sleep(1)
                await msg.remove()



    # 3. Créer un message pour afficher les étapes puis la réponse finale
    msg = cl.Message(content="")
    await msg.send()
    
    # 4. Lancer le workflow LangGraph
    try:
        async for event in app.astream(state):
            for node_name, node_state in event.items():
                # Afficher les étapes en temps réel
                if node_name == "supervisor":
                    await msg.stream_token(f"*[Supervisor]* Analyse de la requête...\n")
                elif node_name == "rag_agent":
                    await msg.stream_token(f"*[RAG]* Recherche dans les documents...\n")
                elif node_name == "data_agent":
                    await msg.stream_token(f"*[Data Analyst]* Analyse des données...\n")
                elif node_name == "critic":
                    await msg.stream_token(f"*[Critic]* Vérification de la réponse...\n\n")
                
                # Mettre à jour notre state global
                for key, value in node_state.items():
                    state[key] = value
                    
    except Exception as e:
        msg.content = f"Erreur lors de l'exécution : {str(e)}"
        await msg.update()
        return

    # 5. Afficher la réponse finale
    final_answer = state.get("answer", "Je n'ai pas pu générer de réponse.")
    
    msg.content = f"**Réponse :**\n\n{final_answer}"
    await msg.update()
    
    # --- NOUVEAU : Affichage des graphiques Plotly ---
    if state.get("figures"):
        for fig in state["figures"]:
            # Chainlit sait convertir une figure Plotly en image affichable
            elements = [cl.Plotly(name="Graphique", figure=fig, display="inline")]
            await cl.Message(content="Voici le graphique généré :", elements=elements).send()
    # ------------------------------------------------
    
    # Sauvegarder le state mis à jour
    cl.user_session.set("state", state)