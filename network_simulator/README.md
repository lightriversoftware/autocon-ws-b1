# Network Simulator

Network topology simulator for teaching demonstrations with REST API and visualizations.

## Features

- **48 network nodes** across eastern US with capacity constraints (200-5000 Gbps)
- **200+ connections** using three-phase topology algorithm (spanning tree → hub-spoke → local spokes)
- **100+ routed services** with capacity-aware pathfinding
- **Geographic visualizations** with matplotlib/geopandas
- **REST API** with FastAPI (CRUD operations, analytics, A* routing)
- **SQLite database** with full data persistence

## Quick Start

```bash
# Install dependencies
uv sync

# Start API server
uv run python run_api.py

# API available at:
# - Swagger UI: http://localhost:8003/docs
# - Health: http://localhost:8003/health
```

## Usage

### Generate Network Topology
```bash
uv run python src/main.py
```

Generates:
- `output/network_map.png` - Geographic visualization
- `output/capacity_distribution.png` - Capacity/weight histograms
- `output/connection_map.png` - Network topology diagram
- `data/adjacency_matrix.csv` - Network adjacency export

### Generate Services
```bash
# Generate 100 services (default)
uv run python src/container_init.py

# Custom count
NUM_SERVICES=200 uv run python src/container_init.py
```

### Run Tests
```bash
uv run pytest              # All tests
uv run pytest tests/       # Main test suite only
```

### Database Utilities
```bash
uv run python scripts/verify_database.py        # Validate constraints
uv run python scripts/demo_database_queries.py  # Example queries
uv run python scripts/clear_services.py         # Clear all services
```

## API Endpoints

Base URL: `http://localhost:8003`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/nodes` | GET | List all nodes |
| `/nodes?vendor=Nokia` | GET | Filter nodes |
| `/nodes/{uuid}` | GET | Get node by ID |
| `/edges` | GET | List all edges |
| `/edges/{uuid}` | GET | Get edge by ID |
| `/services` | GET/POST/DELETE | Manage services |
| `/analytics/stats` | GET | Network statistics |
| `/analytics/capacity/summary` | GET | Capacity overview |
| `/routing/compute` | POST | Compute A* route |

See `/docs` for interactive API documentation.

## Configuration

Edit `config.json` to adjust:
- **gamma**: Capacity importance (0.0 = ignore capacity)
- **beta**: Distance penalty (higher = favor nearby connections)
- **target_edges**: Number of connections (~200)
- **demand_gbps**: Service bandwidth (5 Gbps)
- **target_services**: Number of services (~100)

## Architecture

```
network_simulator/
├── src/
│   ├── api/              # FastAPI REST API
│   ├── core/             # Network simulation logic
│   ├── database/         # SQLite database layer
│   ├── services/         # Service routing algorithms
│   ├── visualization/    # Plot generation
│   └── main.py          # Simulator entry point
├── tests/               # Pytest test suite
├── scripts/             # Database utilities
├── data/                # SQLite DB + CSV files
├── output/              # Generated visualizations
└── config.json          # Algorithm parameters
```

## Data Model

- **Nodes**: UUID, name, vendor, capacity, lat/lon
- **Edges**: UUID, node pairs, capacity, residual capacity
- **Services**: UUID, source/dest nodes, path, bandwidth

All entities use UUIDs. Capacity tracking via pre-computed utilization.

## Algorithm Overview

### Connection Building (3 phases)
1. **Spanning Tree**: Ensure connectivity with capacity-aware MST
2. **Hub-Spoke**: Greedy augmentation favoring high-capacity pairs
3. **Local Spokes**: Connect non-hub nodes to nearby hubs

### Service Routing (2 stages)
A. **Edge Cover**: Guarantee every node is service endpoint
B. **Randomized Routing**: Dijkstra with capacity-based costs

See `config.json` comments for tuning parameters.

## Development

```bash
# Project uses UV for dependency management
uv sync                   # Install dependencies
uv run python <script>    # Run scripts
uv run pytest             # Run tests
```

Requires Python ≥3.12.
