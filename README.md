# Totia

**The Autonomous Discord AI Agent with Semantic Memory and Dynamic Tool-Calling.**

Totia is a high-performance Discord companion that evolves from a simple LLM wrapper into a stateful AI agent. It intelligently searches the web, retrieves channel metadata, and navigates chat history to provide context-aware, style-matched responses.

---

## What Is This?

Totia is an **adaptive AI agent** that uses a "Think-Act-Observe" loop to interact with users. It implements:

- **Autonomous Tool-Calling** — Real-time web searching, history retrieval, and metadata fetching.
- **SQLite Vector Memory** — Infinite-scale semantic recall using local `sentence-transformers` stored in highly compressed binary BLOBs to bypass API quotas.
- **Organic Personality Vibe** — Stripped of corporate cringe and emoji spam, mirroring the user's natural lowercase typing style accurately.
- **High-Availability AI Failover** — Primary intelligence via **Groq (Llama-3)** with real-time tool error interception. If quotas exceed, instantly falls back to **Google Gemini**.
- **Render-Ready Architecture** — Internal health-check server and self-ping keep-alive for zero-downtime hosting.

---

## System Architecture

| Component | Responsibility |
| :--- | :--- |
| [bot.py](totia/bot.py) | **Transport Layer** — Handles Discord gateway events and HTTP health checks. |
| [client.py](totia/client.py) | **Intelligence Layer** — Orchestrates the LLM tool-calling loop (Think-Act-Observe). |
| [tools.py](totia/tools.py) | **Domain Layer** — Encapsulates capabilities with strict Pydantic typings to mitigate LLM hallucinations. |
| [memory.py](totia/memory.py) | **Persistence Layer** — SQLite transactional database managing local vector arrays. |
| [history.py](totia/history.py) | **Buffer Layer** — Manages rolling short-term chat window context. |

---

## Technical Capabilities

### Agent Tools Reference

| Tool | Purpose | Output |
| :--- | :--- | :--- |
| `searchWeb` | Real-time DuckDuckGo information retrieval. | Formatted web snippets. |
| `searchChannel` | Contextual keyword/user search in recent history. | Message log snapshots. |
| `getChannelInfo` | Retrieval of current channel IDs and metadata. | Channel properties. |
| `getServerInfo` | Retrieval of guild stats and member count. | Server properties. |
| `clearMemory` | Administrative reset of user-specific vector store. | Status message. |
| `getCurrentTime` | Synchronization with real-world time-awareness. | Formatted timestamp. |

---

## Deployment & Setup

### Requirements
- **Python 3.10+** (standard for stable Render/Linux environments).
- **Dependencies**: Pruned [requirements.txt](requirements.txt) (only 15 core packages).

### Local Development

```bash
# Clone and enter the repository
cd totia

# Install dependencies in a venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the bot
python -m totia
```

### Render.com Configuration

Totia is built for Render's Free Tier with a built-in "Keep-Alive" heartbeat:

1. **Start Command**: `python -m totia`
2. **Health Check Port**: `8080` (or `$PORT`)
3. **Keep-Alive**: Set `RENDER_URL` in the dashboard to your app's link (e.g. `https://totia.onrender.com`) to enable the rhythmic self-ping.

---

## Configuration Reference

| Variable | Type | Description |
| :--- | :--- | :--- |
| `DISCORD_TOKEN` | Secret | Your Discord Bot application token. |
| `CHANNEL_ID` | Number | The target channel for bot activity. |
| `LLM_PROVIDER` | Enum | `gemini` or `groq`. |
| `GEMINI_API_KEY` | Secret | Required if `LLM_PROVIDER=gemini`. |
| `GROQ_API_KEY` | Secret | Required if `LLM_PROVIDER=groq`. |
| `RENDER_URL` | URL | Your public app URL for self-ping logic. |

---

> [!NOTE]
> **Coding Standard**: Totia uses `camelCase` for all variables and functions. Strict minimalism and zero redundant comments are enforced repository-wide.
