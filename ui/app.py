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
        content="👋 Bienvenue sur **Finance-Agent** !\n\n"
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
                
                chunks = await cl.make_async(load_pdf)(element.path)
                await cl.make_async(index_documents)(chunks)
                
                state["files"].append(element.name)
                msg.content = f"PDF `{element.name}` indexé avec succès !"
                await msg.update()
                await asyncio.sleep(1)
                await msg.remove()
                
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

    # 3. Lancer le workflow LangGraph
    # On affiche un petit indicateur de chargement le temps que ça réfléchisse
    async with cl.Step(name="Analyse en cours...", type="run") as step:
        try:
            async for event in app.astream(state):
                for node_name, node_state in event.items():
                    # Afficher les étapes SEULEMENT dans le terminal
                    if node_name == "supervisor":
                        print(f"[Supervisor] Analyse de la requête...")
                    elif node_name == "rag_agent":
                        print(f"[RAG] Recherche dans les documents...")
                    elif node_name == "data_agent":
                        print(f"[Data Analyst] Analyse des données...")
                    elif node_name == "critic":
                        print(f"[Critic] Vérification de la réponse...")
                    
                    # Mettre à jour notre state global
                    for key, value in node_state.items():
                        state[key] = value
                        
        except Exception as e:
            await cl.Message(content=f"Erreur lors de l'exécution : {str(e)}").send()
            return

    # 4. Afficher la réponse finale
    final_answer = state.get("answer", "Je n'ai pas pu générer de réponse.")
    
    # On affiche le texte directement dans le chat (sans cadre)
    await cl.Message(content=final_answer).send()
    
    # 5. Affichage des graphiques Plotly
    if state.get("figures"):
        for fig in state["figures"]:
            elements = [cl.Plotly(name="Graphique", figure=fig, display="inline")]
            await cl.Message(content="", elements=elements).send()
    
    # 6. Sauvegarder le state mis à jour
    cl.user_session.set("state", state)