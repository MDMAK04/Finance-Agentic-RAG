import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI 

load_dotenv()

# 1. Le LLM principal (Local via Ollama)
def get_llm():
    return ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen2.5:7b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0
    )

# 2. Le modèle pour les embeddings (Local via Ollama)
def get_embeddings():
    return OllamaEmbeddings(
        model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )

# 3. Le LLM "Juge" pour RAGAS (Cloud via API pour plus de fiabilité)
def get_judge_llm():
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0
    )