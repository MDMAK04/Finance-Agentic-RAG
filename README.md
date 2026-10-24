<div align="center">

# 💹 Finance-Agent

**Un assistant financier multi-agents propulsé par LangGraph, LangChain et Ollama.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3-green.svg)](https://python.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-red.svg)](https://qdrant.tech/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 📖 À propos du projet

**Finance-Agent** est un système RAG (Retrieval-Augmented Generation) agentique conçu pour analyser des rapports financiers (PDF) et des données de marché (CSV/Excel). 

Contrairement à un simple chatbot, ce système utilise un **Superviseur intelligent** qui décide dynamiquement quel agent doit répondre à la requête. Il est également doté d'une **Sandbox de sécurité** pour exécuter le code généré par l'IA sans risque, et d'un **Agent Critique** pour vérifier la qualité des réponses.

<div align="center">
  <img src="docs/screenshot_main.png" alt="Interface Finance-Agent" width="800"/>
  <p><i>Interface Chainlit avec génération de graphiques et tableaux dynamiques.</i></p>
</div>

## ✨ Fonctionnalités Clés

- 🧠 **Architecture Multi-Agents (LangGraph)** : Routage intelligent des requêtes via un Superviseur.
- 📄 **RAG Agent** : Recherche sémantique dans les PDFs via Qdrant et embeddings locaux.
- 📊 **Data Analyst Agent** : Génération de code Python (Pandas/Plotly) pour analyser des CSV et créer des graphiques interactifs.
- 🛡️ **Exécution Sécurisée (Sandbox)** : Blocage strict des imports dangereux (`os`, `subprocess`) lors de l'exécution du code LLM.
- 🔍 **Auto-Correction (Critic)** : Vérification et validation des réponses avant affichage.
- 🔒 **Local-First** : Confidentialité totale des données (Ollama + Qdrant locaux).

## 🏗️ Architecture du Système

```text
                        USER
                          ↓
              Question + fichiers (PDF, CSV)
                          ↓
                  ┌───────────────┐
                  │   SUPERVISOR  │
                  └───────┬───────┘
                          ↓
          ┌───────────────┼───────────────┐
          ↓               ↓               ↓
     ┌─────────┐    ┌──────────┐    ┌──────────┐
     │   RAG   │    │   DATA   │    │ GENERAL  │
     │  AGENT  │    │ ANALYST  │    │  CHAT    │
     └────┬────┘    └────┬─────┘    └────┬─────┘
          ↓              ↓               ↓
      PDF texte      CSV/Excel        Conversation
          │              │
          │              ↓
          │        ┌──────────┐
          │        │ SANDBOX  │
          │        └────┬─────┘
          │             ↓
          └──────────────┼───────────────┘
                         ↓
                  ┌──────────────┐
                  │ SYNTHESIZER  │
                  └──────┬───────┘
                         ↓
                  ┌──────────────┐
                  │    CRITIC    │
                  └──────┬───────┘
                         ↓
                 Bonne réponse ?
                  ┌──────┴──────┐
                  ↓             ↓
                 OUI           NON (Retry)
                  ↓             ↓
                 FIN      Retour SUPERVISOR
```

## 🛠️ Stack Technique

| Catégorie | Technologies |
|---|---|
| Orchestration | LangGraph, LangChain |
| LLM (Local) | Ollama (qwen2.5:7b) |
| LLM (Évaluation) | Groq (openai/gpt-oss-120b) |
| Embeddings | Ollama (nomic-embed-text) |
| Vector DB | Qdrant |
| Data / Viz | Pandas, Plotly |
| Interface | Chainlit |
| Sécurité | Sandbox locale (blocage d'imports) |

## 📊 Évaluation (RAGAS)

Afin de valider la fiabilité du système, une évaluation a été menée sur un "Golden Set" de questions (RAG, Data, General) en utilisant Groq comme LLM Juge.

| Métrique | Score | Analyse |
|---|---|---|
| Answer Relevancy | 88.28% | Le système répond de manière très pertinente aux questions posées. |
| Faithfulness | 50.00% | Le système a tendance à halluciner légèrement (limite du modèle 7B local). Amélioration : passer à un modèle 14B ou ajuster le prompt. |
| Context Precision | 40.00% | La recherche vectorielle ramène parfois du bruit. Amélioration : ajouter un Reranker (ex: Cohere) pour filtrer les chunks. |

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.11+
- Docker
- Ollama (installé et lancé)

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/MDMAK04/finance-agentic-rag.git
cd finance-agentic-rag

# 2. Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Télécharger les modèles Ollama
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

### Configuration

Copie le fichier d'exemple et ajoute ta clé API Groq (nécessaire uniquement pour l'évaluation) :

```bash
cp .env.example .env
```

### Lancement

```bash
# 1. Lancer Qdrant en arrière-plan
docker compose up qdrant -d

# 2. Lancer l'interface Chainlit
chainlit run ui/app.py -w
```

Ouvrez http://localhost:8000 dans votre navigateur.

## 📁 Structure du Projet

```text
finance-agentic-rag/
├── agents/                  # Les agents (Supervisor, RAG, Data, Critic)
├── core/                    # Infrastructure (Graph, LLM, Ingestion, Sandbox)
├── evaluation/              # Scripts RAGAS et Golden Set
├── ui/                      # Interface Chainlit
├── data/                    # PDFs et CSV de test
├── docs/                    # Captures d'écran
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 👤 Auteur

**EL Makhloufi Mohammed**

- 🌐 GitHub
- 💼 LinkedIn