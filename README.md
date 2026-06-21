<div align="center">

<img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/OpenAI_Agents_SDK-0.17.5-412991?style=for-the-badge&logo=openai&logoColor=white" />
<img src="https://img.shields.io/badge/Gemini-API-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white" />
<img src="https://img.shields.io/badge/Tavily-Search-FF6B35?style=for-the-badge&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />

# 🔍 Agentic Researcher

### A coordinated pipeline of specialized AI agents — Planner, Researcher, and Writer — that autonomously delivers deep, structured research reports from a single query.

*Drop in a topic. Get back a fully researched, well-structured report — planned, searched, and written autonomously.*

[Features](#-features) · [Architecture](#-architecture) · [Installation](#-installation) · [Usage](#-usage) · [Configuration](#-configuration) · [Project Structure](#-project-structure) · [Roadmap](#-roadmap)

</div>

---

## 📖 Overview

**Agentic Researcher** is a fully autonomous AI research pipeline that takes a single query and produces a detailed, well-structured research report — without you lifting a finger after hitting Enter.

It uses a **multi-agent architecture** where three specialized agents collaborate in sequence:

- 🗺️ A **Planner** breaks your topic into a focused research strategy
- 🔎 A **Researcher** hits the live web via Tavily to gather up-to-date sources
- ✍️ A **Writer** synthesizes everything into a clean, readable report

All of this is orchestrated by a central supervisor agent built on the **OpenAI Agents SDK (v0.17.5)**, running on **Google Gemini** models via Gemini's OpenAI-compatible endpoint.

> Think of it as hiring a research assistant who never sleeps, never skips sources, and always delivers on time.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Multi-Agent Orchestration** | Planner, Researcher, and Writer agents each own a distinct phase of the pipeline |
| 🔎 **Live Web Search** | Powered by Tavily API — results are current, not cached |
| 🛡️ **Input Guardrails** | Validates and filters queries before they enter the pipeline |
| 📝 **Conversation History** | Research context is persisted in `conversation_history.txt` across sessions |
| ⚙️ **Configurable Models** | Swap Gemini models for any agent via a single `model.py` file |

---

## 🏗️ Architecture

The system uses a **supervisor → specialist** pattern. A main orchestrator delegates to three agents in a strict sequence, each passing its output as context to the next.

```
User Query
    │
    ▼
┌──────────────────────────────────────┐
│        Main Agent (Supervisor)       │
│  Orchestrates the full pipeline and  │
│  manages context between agents      │
└──────────┬───────────────────────────┘
           │
    ┌──────▼──────┐
    │   Planner   │  ← Decomposes the query into a structured research plan
    └──────┬──────┘         (subtopics, search angles, scope)
           │
    ┌──────▼──────┐
    │ Researcher  │  ← Executes web searches via Tavily @function_tool
    └──────┬──────┘         (live results, ranked by relevance)
           │
    ┌──────▼──────┐
    │   Writer    │  ← Synthesizes findings into a final markdown report
    └─────────────┘         (structured, cited, human-readable)
```

Each agent is isolated — it only sees what it needs. This keeps outputs focused and reduces hallucination risk.

---

## 📦 Tech Stack

| Package | Version | Role |
|---|---|---|
| `openai-agents` | 0.17.5 | Multi-agent framework and run loop (model-agnostic — pointed at Gemini below) |
| `google-genai` / `openai` | latest | Gemini client — used via Gemini's OpenAI-compatible endpoint |
| `tavily-python` | 0.7.26 | Live web search API |
| `pydantic-settings` | 2.14.1 | `.env` configuration management |
| `python-dotenv` | 1.2.2 | Environment variable loading |

> **Models:** This project uses **Google Gemini models** (default: `gemini-2.5-flash`). Model selection is configured in `model.py`.
>
> **How Gemini is wired in:** the OpenAI Agents SDK talks to Gemini through Gemini's OpenAI-compatible endpoint — point the SDK's OpenAI client at `base_url="https://generativelanguage.googleapis.com/v1beta/openai/"` with your `GEMINI_API_KEY` as the API key, then pass Gemini model names (e.g. `gemini-2.5-flash`, `gemini-3.5-flash`) — no other code changes needed.

---

## ⚡ Installation

### Prerequisites

- Python **3.12+**
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package manager (recommended)
- API keys for [Google AI Studio / Gemini](https://aistudio.google.com/apikey) and [Tavily](https://app.tavily.com/)

### Steps

**1. Clone the repository**

```bash
git clone https://github.com/your-username/Agentic_Researcher.git
cd Agentic_Researcher
```

**2. Install dependencies**

Using `uv` (recommended):
```bash
uv sync
```

Or with pip:
```bash
pip install openai-agents tavily-python pydantic-settings python-dotenv
```

**3. Set up environment variables**

```bash
cp .env.example .env
```

Then fill in your keys (see [Configuration](#-configuration) below).

---

## 🚀 Usage

```bash
uv run python main.py
```

You'll be prompted for a research topic. From there, the pipeline runs automatically:

```
Enter your research topic: The impact of large language models on software engineering

[Planner]     Analyzing query and creating research strategy...
[Researcher]  Searching: "LLMs impact on software engineering 2024"
[Researcher]  Searching: "AI code generation developer productivity studies"
[Researcher]  Searching: "GitHub Copilot enterprise adoption rates"
[Writer]      Synthesizing findings into final report...

✅ Research complete. Report saved to conversation_history.txt
```

### Sample Output Structure

The Writer agent produces a structured report along these lines:

```
# The Impact of Large Language Models on Software Engineering

## Executive Summary
...

## 1. Code Generation & Developer Productivity
...

## 2. Current Adoption Landscape
...

## 3. Limitations and Open Challenges
...

## Sources
- [1] ...
- [2] ...
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file at the project root:

```env
# Required — Gemini API key for all agents
GEMINI_API_KEY=AIza...

# Required — Tavily API key for web search
TAVILY_API_KEY=tvly-...
```

Get your keys here:
- Gemini: https://aistudio.google.com/apikey
- Tavily: https://app.tavily.com/

### Model Configuration

Edit `model.py` to change which Gemini model each agent uses, and to point the OpenAI Agents SDK at Gemini:

```python
# model.py
from openai import AsyncOpenAI
from agents import set_default_openai_client, set_default_openai_api, set_tracing_disabled

# Point the SDK's OpenAI client at Gemini's OpenAI-compatible endpoint
gemini_client = AsyncOpenAI(
    api_key="YOUR_GEMINI_API_KEY",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
set_default_openai_client(gemini_client)
set_default_openai_api("chat_completions")
set_tracing_disabled(True)  # tracing expects an OpenAI key, so disable it for Gemini

MODEL = "gemini-2.5-flash"             # Used by Main Agent, Planner, and Writer
RESEARCHER_MODEL = "gemini-2.5-flash"  # Used by the Researcher agent
```

You can use any Gemini model available through the API (e.g. `gemini-2.5-flash-lite` for speed/cost, `gemini-2.5-flash` for heavier reasoning tasks).

---

## 📁 Project Structure

```
Agentic_Researcher/
│
├── core_agents/
│   ├── main_agent.py        # Supervisor — orchestrates the full pipeline
│   ├── planner.py           # Planner — breaks query into a research strategy
│   ├── researcher.py        # Researcher — executes web searches via Tavily
│   └── writer.py            # Writer — synthesizes findings into a final report
│
├── main.py                  # Entry point — run this to start a research session
├── tool.py                  # Tool definitions — Tavily search registered as @function_tool
├── model.py                 # Model config — Gemini client + model names per agent
├── guardrail.py             # Input validation — filters bad or off-scope queries
│
├── conversation_history.txt # Persisted conversation context across sessions
├── pyproject.toml           # Project metadata and dependencies
├── uv.lock                  # Locked dependency versions (uv)
├── .env.example             # Template for environment variables
└── .python-version          # Pinned Python version (3.12)
```

---

## 🔌 Tools & Guardrails

### `tool.py` — Tavily Search

The Tavily search tool is exposed to the Researcher agent using the OpenAI Agents SDK's `@function_tool` decorator. This makes it a first-class callable tool within the agent pipeline.

| Tool | Provider | Description |
|---|---|---|
| `search_web` | Tavily | Searches the live web and returns ranked results for a query |

### `guardrail.py` — Input Validation

Before any agent runs, incoming queries are validated by the guardrail layer. Queries that are too vague, potentially harmful, or outside the system's scope are rejected with a clear error — keeping the pipeline clean and focused.

---

## 🤝 Contributing

Contributions are welcome — bug fixes, new tools, or new agent types.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push and open a Pull Request

Please follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages. If you're adding a new agent or tool, include a short description in the PR of what it does and how it fits into the pipeline.

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ using the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) + [Google Gemini](https://ai.google.dev/)

⭐ Star this repo if you found it useful!

</div>
