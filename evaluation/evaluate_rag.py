import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import asyncio
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas.run_config import RunConfig
from ragas.embeddings import LangchainEmbeddingsWrapper

from core.graph import app
from core.llm import get_judge_llm
from core.ingestion import load_csv
from langchain_ollama import OllamaEmbeddings

async def run_evaluation():
    print(" Démarrage de l'évaluation RAGAS...")
    
    # 1. Charger le Golden Set
    with open("evaluation/golden_set.json", "r") as f:
        golden_set = json.load(f)
        
    questions = []
    answers = []
    contexts = []
    ground_truths = []
    
    # On charge le dataframe pour les questions "data"
    df = load_csv("data/csv/test.csv")
    
    # 2. Faire tourner le RAG sur chaque question
    for item in golden_set:
        print(f" Question : {item['question']} (Route : {item['expected_route']})")
        
        state = {
            "question": item["question"],
            "files": [],
            "retry_count": 0,
            "history": []
        }
        
        if item["expected_route"] == "rag":
            state["files"] = ["test.pdf"]
        elif item["expected_route"] == "data":
            state["files"] = ["test.csv"]
            state["dataframe"] = df
            
        result = await app.ainvoke(state)
        
        questions.append(item["question"])
        answers.append(result.get("answer", ""))
        ground_truths.append(item["ground_truth"])
        
        if result.get("documents"):
            contexts.append([doc.page_content for doc in result["documents"]])
        else:
            contexts.append(["Pas de contexte"])
        
    # 3. Créer le dataset pour RAGAS
    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }
    dataset = Dataset.from_dict(data)
    
    print("\n Calcul des métriques (ça peut prendre 1-2 minutes)...")
    
    # Configuration du LLM Juge (Groq)
    judge_llm = get_judge_llm()
    
    # Configuration des embeddings locaux (Ollama) pour RAGAS
    # C'est nécessaire car Groq ne fournit pas d'API d'embeddings
    embedder = OllamaEmbeddings(model="nomic-embed-text")
    ragas_embeddings = LangchainEmbeddingsWrapper(embedder)
    
    # Configuration pour éviter les Timeouts
    run_config = RunConfig(max_workers=1, timeout=60)
    
    try:
        results = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision],
            llm=judge_llm,
            embeddings=ragas_embeddings,  
            run_config=run_config
        )
        
        print("\n Résultats de l'évaluation :")
        print(results)
        
        # Sauvegarder les résultats (conversion en format sérialisable)
        with open("evaluation/results.json", "w") as f:
            json.dump(results.to_pandas().to_dict(), f, indent=4)
        print("Résultats sauvegardés dans evaluation/results.json")
        
    except Exception as e:
        print(f"\n Erreur lors de l'évaluation : {e}")

if __name__ == "__main__":
    asyncio.run(run_evaluation())