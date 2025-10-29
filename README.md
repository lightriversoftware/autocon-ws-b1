# AutoCon Workshop B1

A network simulation and automation workshop project.

## Prerequisites

- **Operating System**: WSL/Linux or macOS
- **uv**: Python package and project manager

## Installation

### Installing uv

Follow the installation instructions for your platform: [uv Installation Guide](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)

Quick install:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

OR (if you do not have curl)

```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

## Project Structure

```
autocon/
├── network_simulator/     # Backend API server
│   ├── src/              # FastAPI application code
│   ├── data/             # SQLite database storage
│   ├── output/           # Generated network diagrams
│   ├── migrations/       # Database schema changes
│   └── scripts/          # Utility scripts (reset DB, etc.)
│
└── workshop/             # Workshop exercises
    ├── network_simulator_client/  # Python client library for API
    ├── solutions/        # Reference solutions for exercises
    └── docs/             # Exercise instructions
```

**network_simulator**: FastAPI server that stores network topology (nodes, edges, services). Run this first - it's the backend for all workshop exercises.

**workshop**: Contains the Python client to interact with the API, plus exercises and solutions for building network automation tools.

See [Network Simulator README](./network_simulator/README.md) and [Workshop README](./workshop/README.md) for detailed setup.
