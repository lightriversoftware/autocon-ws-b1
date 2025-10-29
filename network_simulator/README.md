# Network Simulator

A REST API for managing network topologies with nodes, edges, and services.

## Setup

Install dependencies using [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

Activate the created virtual environment.

```bash
source .venv/bin/activate
```

## Running the Simulator

Start the web server:

```bash
uv run uvicorn api.api:app --host 0.0.0.0 --port 8003 --app-dir src
```

## API Documentation

Once the server is running, view the interactive API documentation in your browser:

- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc
