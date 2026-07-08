<div align="center">

<img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/OpenAI_Agents_SDK-0.17.5-412991?style=for-the-badge&logo=openai&logoColor=white" />
<img src="https://img.shields.io/badge/ChatKit-UI-412991?style=for-the-badge&logo=openai&logoColor=white" />
<img src="https://img.shields.io/badge/Gemini-API-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white" />
<img src="https://img.shields.io/badge/Tavily-Search-FF6B35?style=for-the-badge&logoColor=white" />
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />

# 🔍 Agentic Researcher

### A coordinated pipeline of specialized AI agents — Planner, Researcher, and Writer — that autonomously delivers deep, structured research reports from a single query.

*Drop in a topic. Get back a fully researched, well-structured report — planned, searched, and written autonomously. Use it from the terminal, or chat with it in the browser.*

> 💸 **This project runs entirely on free tiers** — Gemini API and Tavily both offer free tiers generous enough for personal use.

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

You can drive the whole pipeline from the terminal, or through a **ChatKit-powered web chat UI** — a FastAPI server streams agent responses straight into a browser-based chat widget, so the same Planner → Researcher → Writer pipeline is now just a conversation away.

> Think of it as hiring a research assistant who never sleeps, never skips sources, and always delivers on time — and now has an office you can walk into.

---

## 💸 Free to Run

This project is designed to run at **zero cost** for personal and light use:

| Service | Free Tier |
|---|---|
| **Gemini API** | Free via [Google AI Studio](https://aistudio.google.com/apikey) — includes `gemini-2.5-flash` with generous RPM/RPD limits |
| **Tavily Search** | Free tier includes **1,000 searches/month** — plenty for regular research sessions |
| **OpenAI API** | Required only for Agents SDK tracing (not inference). You can skip tracing entirely to avoid any cost — see [Configuration](#-configuration) |

> **No credit card needed to get started.** Get your Gemini and Tavily keys, drop them in `.env`, and you're good to go.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧠 **Multi-Agent Orchestration** | Planner, Researcher, and Writer agents each own a distinct phase of the pipeline |
| 🔎 **Live Web Search** | Powered by Tavily API — results are current, not cached |
| 🛡️ **Input Guardrails** | Validates and filters queries before they enter the pipeline — enforced identically in the CLI and the web UI |
| 💬 **ChatKit Web UI** | A browser-based chat interface, streamed live via a FastAPI + ChatKit server sitting in front of the agent pipeline |
| 📝 **Conversation History** | CLI sessions persist context via SQLite (`context.db`); the web UI persists threads and messages in a ChatKit store |
| ⚙️ **Configurable Models** | Swap Gemini models for any agent via a single `model.py` file |
| 💸 **Free to Use** | Runs entirely on free-tier APIs — no billing setup required for personal use |

---

## 🏗️ Architecture

The system uses a **supervisor → specialist** pattern. A main orchestrator delegates to three agents in a strict sequence, each passing its output as context to the next. The pipeline is now fronted by two interchangeable entry points — a CLI and a ChatKit web server — that both drive the same agent graph.

```
                     ┌────────────────────┐        ┌──────────────────────┐
                     │   CLI (main.py)    │        │  Browser (index.html)│
                     └──────────┬─────────┘        └──────────┬────────────┘
                                │                              │ ChatKit widget
                                │                              ▼
                                │                  ┌──────────────────────────┐
                                │                  │  chatkit_app.py (FastAPI)│
                                │                  │  POST /chatkit — SSE     │
                                │                  └──────────┬────────────────┘
                                │                              │
                                │                  ┌──────────────────────────┐
                                │                  │ chatkit_server.py         │
                                │                  │ ResearchChatKitServer     │
                                │                  │ streams agent events,     │
                                │                  │ tracks active_agent       │
                                │                  └──────────┬────────────────┘
                                │                              │
                                │                  ┌──────────────────────────┐
                                │                  │ chatkit_store.py          │
                                │                  │ MemoryStore — threads &   │
                                │                  │ items for the ChatKit UI  │
                                │                  └──────────┬────────────────┘
                                │                              │
                                ▼                              ▼
                     ┌──────────────────────────────────────────────┐
                     │            Main Agent (Supervisor)            │
                     │   Orchestrates the full pipeline and manages  │
                     │   context between agents (shared SQLiteSession)│
                     └──────────┬─────────────────────────────────────┘
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

Each agent is isolated — it only sees what it needs. This keeps outputs focused and reduces hallucination risk. On the web side, `ResearchChatKitServer` tracks which agent last responded (`active_agent` in the thread's metadata) so a multi-turn conversation stays routed to the right stage of the pipeline, and guardrail rejections are surfaced as a normal assistant message instead of a crash.

---

## 📦 Tech Stack

| Package | Version | Role |
|---|---|---|
| `openai-agents` | 0.17.5 | Multi-agent framework and run loop (model-agnostic — pointed at Gemini below) |
| `google-genai` / `openai` | latest | Gemini client — used via Gemini's OpenAI-compatible endpoint |
| `tavily-python` | 0.7.26 | Live web search API |
| `chatkit` | latest | OpenAI's ChatKit server/agent bindings — streams `RunResultStreaming` events into ChatKit's thread protocol |
| `fastapi` | latest | Serves the `/chatkit` endpoint and the static web UI |
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
pip install openai-agents tavily-python pydantic-settings python-dotenv chatkit fastapi uvicorn
```

**3. Set up environment variables**

```bash
cp .env.example .env
```

Then fill in your keys (see [Configuration](#-configuration) below).

---

## 🚀 Usage

You can run Agentic Researcher two ways: as a **CLI** session, or as a **ChatKit web app** in your browser.

### CLI

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

### Web (ChatKit)

```bash
uv run uvicorn chatkit_app:app --reload
```

Then open `http://localhost:8000` in your browser. You'll land on a ChatKit chat window with starter prompts, and your messages stream through the same agent pipeline in real time — full responses render token-by-token as the Writer agent produces them, and rejected queries come back as a plain assistant message explaining why.

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
# Required — Gemini API key for all agents (free at aistudio.google.com)
GEMINI_API_KEY=AIza...

# Required — Tavily API key for web search (free tier: 1,000 searches/month)
TAVILY_API_KEY=tvly-...

# Required — OpenAI API key, used only for Agents SDK tracing
# (not used for inference; Gemini handles all model calls)
OPENAI_API_KEY=sk-...
```

Get your free keys here:
- **Gemini** (free): https://aistudio.google.com/apikey
- **Tavily** (free tier): https://app.tavily.com/
- **OpenAI** (optional, tracing only): https://platform.openai.com/api-keys

### Model Configuration

Edit `model.py` to change which Gemini model each agent uses, and to point the OpenAI Agents SDK at Gemini:

```python
# model.py
import os
from agents import AsyncOpenAI, OpenAIChatCompletionsModel
from dotenv import load_dotenv, find_dotenv

load_dotenv()

external_client = AsyncOpenAI(
    api_key = os.getenv("GEMINI_API_KEY"),
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
)

high_model = OpenAIChatCompletionsModel(
    model = "gemini-2.5-flash",
    openai_client=external_client
)

low_model = OpenAIChatCompletionsModel(
    model = "gemini-2.5-flash-lite",
    openai_client = external_client
)
```

You can use any Gemini model available through the API (e.g. `gemini-2.5-flash-lite` for speed/cost, `gemini-2.5-flash` for heavier reasoning tasks). Both are available on the free tier.

### ChatKit Server Configuration

`chatkit_server.py` wires the agent pipeline into ChatKit's streaming protocol:

- **`AGENTS_BY_NAME`** maps agent names to their instances (`Triage_Agent`, `Planner_Agent`, `Researcher_Agent`, `Writer_Agent`) so the server can resume a thread with the correct agent.
- **Shared session** — a single `SQLiteSession` (`context.db`) backs every ChatKit thread, keeping conversational memory consistent with the CLI's session handling.
- **`MemoryStore`** (`chatkit_store.py`) is an in-memory implementation of ChatKit's `Store` interface — it holds threads and thread items for the lifetime of the process. Swap it for a persistent store (e.g. backed by SQLite or Postgres) if you need threads to survive a restart.
- Attachment support (`save_attachment` / `load_attachment` / `delete_attachment`) is stubbed out and not yet implemented.

The static UI is served straight off the FastAPI app:

```python
app.mount("/", StaticFiles(directory="UI", html=True), name="static")
```

So `index.html` (and any other front-end assets) should live in a `UI/` directory at the project root.

---

## 📁 Project Structure

```
Agentic_Researcher/
│
├── core_agents/
│   ├── main_agent.py        # Supervisor — orchestrates the full pipeline
│   ├── planner.py           # Planner — breaks query into a research strategy
│   ├── researcher.py        # Researcher — executes web searches via Tavily
│   └── writter.py           # Writer — synthesizes findings into a final report
│
├── UI/
│   └── index.html            # ChatKit web UI — mounted as static files by chatkit_app.py
│
├── main.py                  # CLI entry point — run this to start a research session in the terminal
├── chatkit_app.py           # FastAPI app — exposes POST /chatkit and serves the web UI
├── chatkit_server.py        # ResearchChatKitServer — streams agent responses into ChatKit's thread protocol
├── chatkit_store.py         # MemoryStore — in-memory ChatKit Store implementation (threads & items)
├── tool.py                  # Tool definitions — Tavily search registered as @function_tool
├── model.py                 # Model config — Gemini client + model names per agent
├── guardrail.py             # Input validation — filters bad or off-scope queries
│
├── conversation_history.txt # Persisted CLI conversation context across sessions
├── context.db                # Shared SQLite session store (CLI + ChatKit)
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

Before any agent runs, incoming queries are validated by the guardrail layer. Queries that are too vague, potentially harmful, or outside the system's scope are rejected with a clear error — keeping the pipeline clean and focused. In the ChatKit server, a tripped guardrail (`InputGuardrailTripwireTriggered`) is caught and returned as a normal assistant message explaining the rejection reason, so the chat UI never just hangs or errors out.

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

Built with ❤️ using the [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) + [ChatKit](https://github.com/openai/chatkit-python) + [Google Gemini](https://ai.google.dev/)

⭐ Star this repo if you found it useful!

</div>
