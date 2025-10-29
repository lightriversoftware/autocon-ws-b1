# Setup Guide

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- Azure OpenAI credentials

## Quick Setup

### 1. Start Network Simulator

```bash
cd network_simulator
uv sync
source .venv/bin/activate
uv run uvicorn api.api:app --host 0.0.0.0 --port 8003 --app-dir src
```

Verify: http://localhost:8003/health

### 2. Setup Workshop Environment

```bash
cd workshop
uv sync
source .venv/bin/activate
```

### 3. Configure Credentials

Edit `.env` file in `workshop/` directory:

```
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
BACKEND_URL=http://localhost:8003
```

### 4. Verify Setup

```bash
python ex0_verify_setup.py
```

If all checks pass, you're ready.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| API won't connect | Start simulator: `cd network_simulator && uv run uvicorn...` |
| Import errors | Activate workshop venv: `source .venv/bin/activate` |
| Missing credentials | Check `.env` file has all Azure OpenAI variables |

## Next Steps

See [EXERCISE_GUIDE.md](EXERCISE_GUIDE.md) to start building agents.
