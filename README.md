# Finance-Agent

> A multi-agent RAG system for financial analysis powered by LangGraph, LangChain, Ollama, and Qdrant.

## 🎯 Overview

Finance-Agent is an agentic AI system that analyzes financial documents (annual reports, PDFs) and market data (CSV, Excel) to answer complex financial questions.

It uses a **Supervisor** to route queries to specialized agents:
- **RAG Agent** — retrieves information from PDF documents
- **Data Analyst Agent** — analyzes CSV/Excel with Pandas
- **General Agent** — handles conversational queries

A **Critic** verifies every answer and triggers a retry loop if needed.

