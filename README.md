## Quick Start

The easiest way to run the network simulator is using the pre-built Docker image:

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/)
- [Git](https://git-scm.com/)

### Run Network Simulator
```bash
# Pull the latest network simulator image
docker pull ghcr.io/lightriversoftware/network_simulator:latest

# Create directories for persistent data
mkdir -p ./data ./output

# Run the network simulator
docker run -d \
  --name network-simulator \
  -p 8003:8003 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  -e FORCE_REBUILD=false \
  -e SKIP_VERIFICATION=false \
  -e GENERATE_SERVICES=true \
  -e NUM_SERVICES=100 \
  ghcr.io/lightriversoftware/network_simulator:latest

# Verify it's running
curl http://localhost:8003/health
```

That's it! The network simulator is now running on http://localhost:8003

## Building from Source (Optional)

If you want to build the Docker image locally instead of using the pre-built image:

```bash
# Clone the repository
git clone <repository-url>
cd autocon-ws-b1

# Build the Docker image
docker build -f Dockerfile.network_simulator -t network_simulator:local .

# Run the locally built image
docker run -d \
  --name network-simulator \
  -p 8003:8003 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  -e FORCE_REBUILD=false \
  -e SKIP_VERIFICATION=false \
  -e GENERATE_SERVICES=true \
  -e NUM_SERVICES=100 \
  network_simulator:local
```

## Environment Variables

The network simulator supports several configuration options:

| Variable | Default | Description |
|----------|---------|-------------|
| `FORCE_REBUILD` | `false` | Force rebuild of network data |
| `SKIP_VERIFICATION` | `false` | Skip database verification |
| `GENERATE_SERVICES` | `true` | Generate network services |
| `NUM_SERVICES` | `100` | Number of services to generate |

## API Access

Once the network simulator is running:
- **API Base URL**: `http://localhost:8003`
- **Health Check**: `http://localhost:8003/health`
- **API Documentation**: `http://localhost:8003/docs`
- **OpenAPI Spec**: `http://localhost:8003/openapi.json`

## Docker Management

```bash
# View logs
docker logs network-simulator

# Stop the simulator
docker stop network-simulator

# Remove the container
docker rm network-simulator

# Update to latest image
docker pull ghcr.io/shivam-patel-lr/network_simulator:latest
docker stop network-simulator
docker rm network-simulator
# Then run the docker run command again
```