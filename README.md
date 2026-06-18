<div align="center">

<img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/OpenAI_Agents_SDK-0.17.5-412991?style=for-the-badge&logo=openai&logoColor=white" />
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

All of this is orchestrated by a central supervisor agent built on the **OpenAI Agents SDK (v0.17.5)**.

> Think of it as hiring a research assistant who never sleeps, never skips sources, and always delivers on time.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Multi-Agent Orchestration** | Planner, Researcher, and Writer agents each own a distinct phase of the pipeline |
| 🔎 **Live Web Search** | Powered by Tavily API — results are current, not cached |
| 🛡️ **Input Guardrails** | Validates and filters queries before they enter the pipeline |
| 📝 **Conversation History** | Research context is persisted in `conversation_history.txt` across sessions |
| ⚙️ **Configurable Models** | Swap OpenAI models for any agent via a single `model.py` file |

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
| `openai-agents` | 0.17.5 | Multi-agent framework and run loop |
| `openai` | 2.41.1 | OpenAI API client (GPT models) |
| `tavily-python` | 0.7.26 | Live web search API |
| `pydantic-settings` | 2.14.1 | `.env` configuration management |
| `python-dotenv` | 1.2.2 | Environment variable loading |

> **Models:** This project uses **OpenAI GPT models** (default: `gpt-4o`). Model selection is configured in `model.py`.

---

## ⚡ Installation

### Prerequisites

- Python **3.12+**
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package manager (recommended)
- API keys for [OpenAI](https://platform.openai.com/api-keys) and [Tavily](https://app.tavily.com/)

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
# Required — OpenAI API key for all agents
OPENAI_API_KEY=sk-...

# Required — Tavily API key for web search
TAVILY_API_KEY=tvly-...
```

Get your keys here:
- OpenAI: https://platform.openai.com/api-keys
- Tavily: https://app.tavily.com/

### Model Configuration

Edit `model.py` to change which OpenAI model each agent uses:

```python
# model.py
MODEL = "gpt-4o"             # Used by Main Agent, Planner, and Writer
RESEARCHER_MODEL = "gpt-4o"  # Used by the Researcher agent
```

You can use any model available through the OpenAI API (e.g. `gpt-4o-mini` for lower cost, `o1` for heavier reasoning tasks).

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
├── model.py                 # Model config — set OpenAI models per agent here
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

## 🗺️ Roadmap

- [ ] Rich CLI output with progress indicators and formatted report display
- [ ] Export reports as PDF or HTML
- [ ] Additional search tools (Wikipedia, arXiv, news APIs)
- [ ] Caching layer to skip redundant searches on similar queries
- [ ] Source citation tracking and credibility scoring
- [ ] Web UI built with Streamlit or Gradio
- [ ] Async parallel search across multiple queries simultaneously

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

Built with ❤️ using the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)

⭐ Star this repo if you found it useful!

</div>
