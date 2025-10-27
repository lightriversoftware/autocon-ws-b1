# Network Agents Workshop

This repository contains hands-on exercises for building AI agents that interact with network infrastructure through a simulated network environment. Participants will learn to create agents for network support, planning, and provisioning tasks.

## Workshop Overview

The workshop covers practical exercises to explore AI agent development patterns

**What You'll Do:** Complete exercises in `net_agents/workshop/` by filling in docstrings and implementing agent logic. The workshop requires only UV and Docker installation before you can begin.

## Prerequisites & Installation

Before starting the workshop, you'll need to install two tools: **UV** (Python package manager) and **Docker**. Follow the instructions for your operating system below.

### Step 1: Install UV Python Package Manager

UV is a fast Python package manager that we'll use for dependency management.

#### Windows (including WSL)

**If using WSL (Windows Subsystem for Linux)** - recommended for this workshop:

1. Open your WSL terminal
2. Run the Linux installation command below

**If using Windows directly:**

1. Open PowerShell
2. Run:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

#### Mac

1. Open Terminal
2. Run:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

**Alternative:** If you have Homebrew installed:

```bash
brew install uv
```

#### Linux / WSL

1. Open your terminal
2. Run:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

#### Verify UV Installation

After installation, close and reopen your terminal, then verify:

```bash
uv --version
```

You should see a version number printed (e.g., `uv 0.5.1` or similar).

### Step 2: Install Docker

Docker allows us to run the network simulator and workshop environment in isolated containers.

#### Windows

**Recommended:** Install Docker Desktop for an easy setup experience.

1. Download Docker Desktop from: https://docs.docker.com/desktop/setup/install/windows-install/
2. Run the installer (`Docker Desktop Installer.exe`)
3. Choose **WSL 2** as the backend when prompted (recommended)
4. Complete the installation and restart if needed
5. Launch Docker Desktop from the Start menu
6. Wait for Docker Desktop to start completely

**System Requirements:**

- Windows 10/11 64-bit (Pro, Enterprise, or Education)
- At least 4GB RAM
- WSL 2 installed (run `wsl --install` in PowerShell if not already installed)

#### Mac

**Recommended:** Install Docker Desktop.

1. Download Docker Desktop from: https://docs.docker.com/desktop/setup/install/mac-install/
   - Choose the version for your chip (Intel or Apple Silicon)
2. Open the downloaded `Docker.dmg` file
3. Drag the Docker icon to your Applications folder
4. Launch Docker from Applications
5. Accept the service agreement
6. Complete the setup (you may need to enter your password)

**System Requirements:**

- macOS (current version or previous two major releases)
- At least 4GB RAM
- For Apple Silicon Macs: Rosetta 2 (install with: `softwareupdate --install-rosetta`)

#### Linux / WSL

**Note for WSL Users:** You can either install Docker Desktop on Windows (which integrates with WSL) or install Docker Engine directly in WSL. Docker Desktop is easier but requires Windows Pro/Enterprise/Education. Docker Engine works on any Windows edition with WSL.

For Linux or WSL users installing Docker Engine directly:

**Ubuntu/Debian:**

1. Set up Docker's package repository:

   ```bash
   # Add Docker's official GPG key
   sudo apt-get update
   sudo apt-get install ca-certificates curl
   sudo install -m 0755 -d /etc/apt/keyrings
   sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
   sudo chmod a+r /etc/apt/keyrings/docker.asc

   # Add repository to Apt sources
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   sudo apt-get update
   ```

2. Install Docker Engine:

   ```bash
   sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
   ```

3. Add your user to the docker group (to run Docker without sudo):

   ```bash
   sudo usermod -aG docker $USER
   ```

4. Log out and log back in (or restart your terminal) for the group change to take effect

**RHEL/Fedora/Other Distributions:**

- RHEL: https://docs.docker.com/engine/install/rhel/
- Debian: https://docs.docker.com/engine/install/debian/
- Other distributions: https://docs.docker.com/engine/install/

#### Verify Docker Installation

After installation, verify Docker is working:

```bash
docker --version
```

You should see a version number printed (e.g., `Docker version 24.0.6` or similar).

Test Docker is running properly:

```bash
docker ps
```

This should show an empty list of containers (no errors). If you see an error, make sure:

- **Windows/Mac:** Docker Desktop is running (check the system tray/menu bar)
- **Linux/WSL:** You've logged out and back in after adding yourself to the docker group

### Step 3: Verify Installation

Run these commands to confirm your setup is complete:

```bash
# Verify UV is installed
uv --version

# Verify Docker is installed
docker --version

# Verify Docker is running
docker ps
```

All three commands should complete without errors. If you encounter any issues, see the troubleshooting section below.

### Common Installation Issues

**UV not found after installation:**

- Close and reopen your terminal
- The installer adds UV to your PATH, which requires a fresh terminal session

**Docker command not found (Linux/WSL):**

- Make sure you logged out and back in after adding yourself to the docker group
- Try: `sudo docker ps` - if this works, you need to restart your session for group changes

**Cannot connect to Docker daemon:**

- **Windows/Mac:** Make sure Docker Desktop is running (check system tray/menu bar)
- **Linux:** Start Docker with: `sudo systemctl start docker`

**Permission denied when running Docker (Linux/WSL):**

- Run: `sudo usermod -aG docker $USER`
- Log out and log back in
- Verify with: `groups` (should include "docker")

### Additional Prerequisite

- [Git](https://git-scm.com/) for cloning the repository

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd autocon-ws-b1

# Start everything with one command
docker-compose up -d

# Enter the workshop environment
docker-compose exec workshop bash

# Verify setup is working
verify-setup
```

That's it! The setup includes:

- Network simulator API running on http://localhost:8003
- Workshop development environment with all dependencies
- Pre-built images (no local building required)
- Persistent data volumes

## Alternative Setup Options

### Option 1: VSCode DevContainer

The easiest way to get started is using the provided VSCode devcontainer that handles all dependencies automatically:

1. **Prerequisites:**

   - [Visual Studio Code](https://code.visualstudio.com/)
   - [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. **Open in DevContainer:**

   ```bash
   # Clone the repository
   git clone <repository-url>
   cd autocon-ws-b1

   # Open in VSCode
   code .
   ```

3. **Start DevContainer:**

   - VSCode should prompt you to "Reopen in Container"
   - Or use Command Palette (Ctrl+Shift+P / Cmd+Shift+P) -> "Dev Containers: Reopen in Container"
   - Wait for the container to build (first time only)

4. **Verify Setup:**
   ```bash
   # In the VSCode terminal inside the container
   cd net_agents
   python ex0_verify_setup.py
   ```

### Option 2: Manual Docker Setup

Pre-built Docker images are available from GitHub Container Registry:

#### Authentication

```bash
# Authenticate with GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

#### Network Simulator

```bash
# Pull and run the network simulator
docker pull ghcr.io/OWNER/network-simulator:latest

# Run with persistent data
mkdir -p ./data ./output
docker run -d \
  --name network-simulator \
  -p 8003:8003 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  ghcr.io/OWNER/network-simulator:latest

# Verify it's running
curl http://localhost:8003/health
```

### Option 3: Local Installation (Not Recommended)

If you prefer to install dependencies locally:

#### Prerequisites

**Python 3.8+ Installation:**

- **macOS**: `brew install python` or download from [python.org](https://python.org)
- **Linux**: `sudo apt install python3 python3-pip` (Ubuntu/Debian) or `sudo yum install python3 python3-pip` (RHEL/CentOS)
- **Windows**: Download from [python.org](https://python.org) or `winget install Python.Python.3`

#### Setup Steps

1. **Create Python Environment:**

   ```bash
   # Verify Python version
   python --version  # or python3 --version on some systems

   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # macOS/Linux:
   source venv/bin/activate

   # Windows (Command Prompt):
   venv\Scripts\activate.bat

   # Windows (PowerShell):
   venv\Scripts\Activate.ps1
   ```

2. **Install Dependencies:**

   ```bash
   # Install main requirements
   pip install -r requirements.txt

   # Install the network client SDK
   cd net_agents
   pip install -e .
   cd ..
   ```

3. **Start Network Simulator:**

   ```bash
   cd network_simulator

   # macOS/Linux:
   python -m uvicorn api.api:app --host 0.0.0.0 --port 8003 --app-dir src

   # Windows:
   python -m uvicorn api.api:app --host 0.0.0.0 --port 8003 --app-dir src
   ```

## Workshop Structure

### Exercises Directory: `net_agents/workshop/`

1. **ex0_verify_setup.py** - Verify your environment is working
2. **ex1_support_agent.py** - Build a network support agent
3. **ex2_planning_agent.py** - Create a network planning agent
4. **ex3_provisioning_agent.py** - Develop a service provisioning agent

### Solutions Directory: `net_agents/workshop/solutions/`

Reference implementations are provided for each exercise.

### Network Simulator Client: `net_agents/network_simulator_client/`

SDK for interacting with the network simulator API. See `net_agents/README.md` for detailed documentation.

## API Access

Once the network simulator is running:

- **API Base URL**: `http://localhost:8003`
- **Health Check**: `http://localhost:8003/health`
- **API Documentation**: `http://localhost:8003/docs`
- **OpenAPI Spec**: `http://localhost:8003/openapi.json`

## Troubleshooting

### Common Issues

1. **Port 8003 Already in Use:**

   ```bash
   # macOS/Linux:
   lsof -i :8003
   kill -9 <PID>

   # Windows:
   netstat -ano | findstr :8003
   taskkill /PID <PID> /F
   ```

2. **DevContainer Won't Start:**

   - Ensure Docker Desktop is running
   - Try: "Dev Containers: Rebuild Container"
   - Check Docker has sufficient resources allocated

3. **Network Simulator Connection Errors:**

   ```bash
   # Check if simulator is running
   docker ps | grep network-simulator

   # View logs
   docker logs network-simulator
   ```

4. **Python Module Import Errors:**

   ```bash
   # Reinstall the client SDK
   cd net_agents
   pip install -e .
   ```

5. **Virtual Environment Issues:**

   ```bash
   # Deactivate current environment
   deactivate

   # Remove and recreate
   rm -rf venv  # or rmdir /s venv on Windows
   python -m venv venv

   # Reactivate and reinstall
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

### Platform-Specific Notes

**macOS:**

- May need to install Xcode command line tools: `xcode-select --install`
- If using M1/M2 Mac, Docker containers will run in emulation mode

**Linux:**

- May need to install additional packages: `sudo apt install build-essential python3-dev`
- Ensure your user is in the docker group: `sudo usermod -aG docker $USER`

**Windows:**

- PowerShell execution policy may need adjustment: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Consider using Windows Terminal for better command line experience
- WSL2 recommended for optimal Docker performance

### Getting Help

- Check the exercise guide: `net_agents/workshop/docs/EXERCISE_GUIDE.md`
- Review network reference: `net_agents/workshop/docs/NETWORK_REFERENCE.md`
- Setup instructions: `net_agents/workshop/docs/SETUP.md`

## Development

### Running Tests

```bash
cd net_agents
pytest
```

### Code Formatting

```bash
# If you want to format code (optional)
black net_agents/
ruff check net_agents/
```

## Architecture

- **Network Simulator**: FastAPI-based REST API simulating network infrastructure
- **Client SDK**: Python library for interacting with the network simulator
- **Workshop Exercises**: Progressive hands-on coding exercises
- **Docker Support**: Containerized deployment for consistency across environments

## Technologies Used

- Python 3.12
- FastAPI for the REST API
- SQLite for data persistence
- Pydantic for data validation
- HTTPX for HTTP client operations
- Docker for containerization
- VSCode DevContainers for development environment

## License

This workshop is part of the AutoCon project.

---

**Ready to start?** Open this repository in VSCode with the Dev Containers extension, or follow the setup instructions above. Begin with `ex0_verify_setup.py` to ensure everything is working correctly.
