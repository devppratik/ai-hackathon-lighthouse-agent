# OC Commands Analyzer Agent

[![Python 3.12+](https://img.shields.io/badge/python-3.12,3.13-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A LangGraph-based AI agent that uses the OC Commands Analyzer MCP Server to help users understand and work with OpenShift CLI commands. **Supports both local Ollama and Google Vertex AI** as LLM providers.

## Features

- **Intelligent OC Command Analysis**: Uses MCP tools to parse and explain OpenShift commands
- **Best Practice Recommendations**: Provides safety and optimization suggestions
- **Resource Documentation**: Access detailed OpenShift resource field documentation
- **Real-time Streaming**: Server-Sent Events (SSE) for responsive interactions
- **Conversation History**: SQLite-based checkpointing for multi-turn conversations
- **Flexible LLM Support**: Works with **Ollama (local)** or **Vertex AI (cloud)**

## Prerequisites

1. **Python 3.12+**
2. **OC Commands Analyzer MCP Server** (must be running)
3. **LLM Provider** (choose one):
   - **Ollama** (local, free): Install from [ollama.com](https://ollama.com)
   - **Vertex AI** (cloud): Google Cloud credentials

## Quick Start

### Option 1: Using Ollama (Local, No API Keys Required) ⭐ Recommended

1. **Install and start Ollama:**
   ```bash
   # Install from https://ollama.com or:
   curl -fsSL https://ollama.com/install.sh | sh

   # Start Ollama (keep running)
   ollama serve

   # Pull a model (in another terminal)
   ollama pull llama3.2
   ```

2. **Start the OC Commands Analyzer MCP Server:**
   ```bash
   cd ../oc-commands-analyzer-mcp-server
   uv venv && source .venv/bin/activate
   uv pip install -e .
   oc-commands-analyzer-mcp-server
   ```

3. **Install and configure the agent:**
   ```bash
   cd ../oc-commands-analyzer-agent
   uv venv && source .venv/bin/activate
   uv pip install -e .

   cp .env.example .env
   # Edit .env and set:
   #   LLM_PROVIDER=ollama
   #   OLLAMA_MODEL=llama3.2
   ```

4. **Run the agent:**
   ```bash
   oc-commands-analyzer-agent
   ```

### Option 2: Using Vertex AI (Google Cloud)

1. **Set up Google Cloud credentials** (one of):
   ```bash
   # Service account file
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"

   # Or use gcloud auth
   gcloud auth application-default login
   ```

2. **Start the MCP Server** (same as Option 1, step 2)

3. **Configure the agent:**
   ```bash
   cd ../oc-commands-analyzer-agent
   uv venv && source .venv/bin/activate
   uv pip install -e .

   cp .env.example .env
   # Edit .env and set:
   #   LLM_PROVIDER=vertex
   #   VERTEX_PROJECT_ID=your-project-id
   #   GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
   ```

4. **Run the agent:**
   ```bash
   oc-commands-analyzer-agent
   ```

## Configuration

### Ollama Setup (Recommended)
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2        # Or: mistral, qwen2.5-coder, etc.
```

**Popular Ollama Models:**
- `llama3.2` (4GB) - Fast, good for general use
- `llama3.1` (8GB) - More capable
- `mistral` (7GB) - Fast and efficient
- `qwen2.5-coder` (7GB) - Optimized for code/commands

Download models: `ollama pull llama3.2`

### Vertex AI Setup
```bash
LLM_PROVIDER=vertex
VERTEX_PROJECT_ID=your-project-id
VERTEX_LOCATION=us-central1
VERTEX_MODEL=gemini-2.0-flash-exp
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

## API Usage

### Health Check
```bash
curl http://localhost:8082/health
```

### Streaming Chat
```bash
curl -X POST "http://localhost:8082/v1/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze: oc get pods -n production",
    "thread_id": "conversation-123"
  }'
```

## Troubleshooting

### Ollama Issues
```bash
# Check if Ollama is running
curl http://localhost:11434

# List installed models
ollama list

# Pull a model
ollama pull llama3.2
```

### Can't connect to MCP Server
```bash
# Check MCP server is running
curl http://localhost:5002/health
```

See full [README](./README.md) for complete documentation.
