# AutoCon

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

### Network Simulator

The `network_simulator/` directory contains the backend webserver for the workshop. This server manages and stores:

- Node information
- Edge (connection) information
- Service information

For detailed information about the network simulator, see the [Network Simulator README](./network_simulator/README.md).

### Workshop

The `workshop/` directory contains the files for the actual workshop, including exercises and solutions.

For workshop setup and exercise instructions, see the [Workshop README](./workshop/README.md).
