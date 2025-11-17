# AutoCon 4 Workshop B1: Building AI Agents for Smarter Networks

Welcome! This repository contains hands-on exercises for building AI agents that interact with network infrastructure through a simulated (and significantly simplified!) network environment. You will learn to create agents that can chat, call tools, run workflows, and communicate with other agents.

Presentor Information:

- Organization: [LightRiver Software](https://lightriver.com/)
- Proctors [Shivam Patel](mailto:spatel@lightriver.com), [Dan Rose](mailto:drose@lightriver.com)

**What You'll Do:** Complete exercises in `workshop/` by filling in the areas marked for each exercise. The workshop requires only UV and a code editor installation before you can begin. Feel free to refer to follow along by using this document.

## Helpful References

- OpenAI Platform Docs: [https://platform.openai.com/docs/overview](https://platform.openai.com/docs/overview)
- OpenAI Agents SDK Docs: [https://openai.github.io/openai-agents-python/](https://openai.github.io/openai-agents-python/)
- OpenAI Cookbooks: [https://cookbook.openai.com/](https://cookbook.openai.com/)

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
```

**network_simulator**: FastAPI server that stores network topology (nodes, edges, services). Run this first - it's the backend for all workshop exercises.

**workshop**: Contains the Python client to interact with the API, plus exercises and solutions for building network automation tools.

## Part 0: Getting Set Up

### Prerequisites & Installation

Before starting the workshop, you'll need to install two tools: **UV** (Python package manager) and a **text editor** or **IDE** of your choice. We recommend using [VSCode](https://code.visualstudio.com/) to edit and interact with the files of the workshop, but again any editor + terminal combination will do. We'll assume you have your development tool/combination installed already. Likewise, we'll assume you also already have [git](https://git-scm.com/install/) installed. You'll need it to clone this repository!

This workshop is designed to be run on Linux or MacOS. You _can_ run it on native Windows if needed, though we recommend using [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install).

#### Step 1: Install UV Python Package Manager

[UV](https://docs.astral.sh/uv/) is a fast Python package manager that we'll use for dependency management. It ensures that you'll be using the right `python` version and combination of dependencies when completing the workshop. UV operates on the concept of virtual environments. A `uv` virtual environment is an isolated, self-contained Python workspace that uv creates and manages to keep a project’s dependencies, interpreter, and tooling separate from the rest of the system.

**Windows**

1. Open PowerShell
2. Run:
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

**Mac**

1. Open Terminal
2. Run:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

_Alternative:_ If you have Homebrew installed:

```bash
brew install uv
```

**Linux / WSL**

1. Open your terminal (If using WSL, note that this is different from you native Windows Shell!)
2. Run:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

**Verify UV Installation**

After installation, close and reopen your terminal, then verify:

```bash
uv --version
```

You should see a version number printed (e.g., `uv 0.8.5` or similar).

#### Step 2: Setup Environment

This workshop has two distinct components, as explained above. The `network_simulator/` exists to provide your agents a system to interact with. It relies on a number of key dependencies, `pandas`, `numpy`, `networkx`, `fastapi`, among others. Similarly, it has no dependency on any of the OpenAI SDK packages that the files in `workshop/` are dependent on. Therefore, we'll create two distinct **virtual environments** to run each of these components. In addition to the right environment/dependencies, we'll also need to set some environment variables in the `workshop/` directory to correctly configure the API calls or files will be making.

**Network Simulator Setup**

```bash
cd <path-to-workshop-files>/autocon-ws-b1/network_simulator
uv venv .venv # this creates a virtual environment in the .venv/ directory
uv sync # this downloads and installs the dependencies in pyproject.toml
```

You should now see a `.venv/` directory within the `network_simulator` directory. Let's activate it and ensure it's working.

```bash
source .venv/bin/activate
which python # This should output a python binary in the network_simulator virtual environment
```

Now, let's run the backend:

```bash
python run_api.py
```

You should see output showing the API server starting:

```
======================================================================
Network Simulator API
======================================================================

Starting FastAPI server...

API Documentation:
  Swagger UI:  http://localhost:8003/docs
  ReDoc:       http://localhost:8003/redoc

Endpoints:
  Health:      GET  http://localhost:8003/health
  Nodes:       GET  http://localhost:8003/nodes
  ...

Press CTRL+C to stop the server
======================================================================

INFO:     Uvicorn running on http://0.0.0.0:8003 (Press CTRL+C to quit)
INFO:     Started server process [12345]
INFO:     Application startup complete.
```

The network simulator is now running! Verify it's working by visiting [http://localhost:8003/docs](http://localhost:8003/docs) in your browser, or test the health endpoint:

```bash
curl http://localhost:8003/health
# Expected: {"status":"healthy","database":"connected", ...}
```

**Important:** Keep this terminal open with the API running. Open a new terminal for the next steps.

**Workshop Setup**

Now let's set up the workshop environment. Open a **new terminal** and navigate to the workshop directory:

```bash
cd <path-to-workshop-files>/autocon-ws-b1/workshop
uv venv .venv
```

You should see:

```
Using CPython 3.12.11
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate
```

Install the dependencies:

```bash
uv sync
```

You'll see packages being installed:

```
Resolved 46 packages in 15ms
Installed 38 packages in 58ms
 + openai==2.5.0
 + openai-agents==0.4.0
 + network-simulator-client==0.1.0
 ...
```

Activate the virtual environment:

```bash
source .venv/bin/activate
which python  # Should show: /path/to/workshop/.venv/bin/python
```

#### Step 3: Configure OpenAI API Credentials

**These credentials will be emailed to you by the workshop proctors.** The email will contain:

- Your API key
- The API endpoint URL
- The model deployment name

Once you receive them:

1. **Create your environment file:**

   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** with the values from your email:

   ```bash
   OPENAI_API_KEY='your-api-key-from-email'
   OPENAI_ENDPOINT='https://your-endpoint-from-email.com/openai/v1/'
   OPENAI_DEPLOYMENT='gpt-4o'  # or model name from email
   BACKEND_URL='http://localhost:8003'
   ```

   **Note:** Keep the single quotes. `BACKEND_URL` should always be `http://localhost:8003`.

#### Step 4: Verify Your Setup

Run the verification script:

```bash
python ex0_verify_setup.py
```

Expected output:

```
============================================================
 Workshop Setup Verification
============================================================

✓ Python 3.12.11
✓ OpenAI Agents SDK installed (version 0.4.0)
✓ OpenAI API key configured (######...####)
✓ OpenAI endpoint configured (https://...)
✓ OpenAI deployment configured (gpt-...)
LLM generation successful!
✓ Network Simulator API: healthy
✓ Network loaded: 48 nodes, 200 edges, 100 services

============================================================
Setup complete! You're ready to start building agents.
```

#### Troubleshooting:

- **API Connection Failed:** Ensure the network simulator is running in your first terminal at `http://localhost:8003`
- **OpenAI API errors:** Verify you copied credentials correctly from your email (no extra spaces or quotes)
- **Module not found:** Activate the workshop virtual environment: `source .venv/bin/activate`
- **Wrong Python version:** Check you're using the venv's Python: `which python`

---

**Common Problems and Solutions**

This section covers issues you might encounter during the workshop. Try these solutions before asking for help!

**Problem: "Address already in use" or port 8003 conflict**

```bash
# Find what's using port 8003
lsof -i :8003  # On Mac/Linux
netstat -ano | findstr :8003  # On Windows

# Kill the process or use a different port
# Edit network_simulator/run_api.py and change port=8003 to another port
# Then update BACKEND_URL in workshop/.env to match
```

**Problem: Network simulator crashes or shows database errors**

```bash
# Check database integrity
cd network_simulator
source .venv/bin/activate
python scripts/verify_database.py

# If database is corrupted, back it up and restart
mv data/network.db data/network.db.backup
# Then restart the API - it should regenerate the database
python run_api.py
```

**Problem: "Module 'api.api' not found"**

```bash
# Make sure you're running from the network_simulator directory
cd network_simulator
source .venv/bin/activate
python run_api.py
```

**Problem: Commands like `openai` or `python` not found after installation**

```bash
# You forgot to activate the virtual environment
source .venv/bin/activate  # Run this in the correct directory
# Verify with:
which python  # Should show path to .venv/bin/python
```

**Problem: "No module named 'openai'" or other import errors**

```bash
# Check you're in the right virtual environment
which python  # Should show workshop/.venv/bin/python

# If wrong, activate the correct environment:
cd workshop
source .venv/bin/activate

# If still broken, reinstall dependencies:
uv sync --reinstall
```

**Problem: Multiple Python versions causing conflicts**

```bash
# UV manages Python versions automatically
# If you have issues, create a fresh virtual environment:
cd workshop  # or network_simulator
rm -rf .venv
uv venv .venv
source .venv/bin/activate
uv sync
```

**Problem: "OPENAI_API_KEY not set" even after editing .env**

```bash
# .env file is only loaded when you run Python scripts
# Verify your .env file exists and has correct format:
cat .env  # Should show: OPENAI_API_KEY='...' with quotes

# Common mistakes:
# ❌ OPENAI_API_KEY=value  (missing quotes)
# ❌ OPENAI_API_KEY = 'value'  (spaces around =)
# ✓ OPENAI_API_KEY='value'  (correct)

# Test loading:
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
```

**Problem: Wrong BACKEND_URL or connection refused**

```bash
# Check the network simulator is running:
curl http://localhost:8003/health

# If it fails, verify the port in both places matches:
# 1. network_simulator/run_api.py (line ~42: port=8003)
# 2. workshop/.env (BACKEND_URL='http://localhost:8003')
```

**Problem: "Invalid API key" or authentication errors**

- Verify you copied the entire key from your email (no spaces at start/end)
- Check the key is within single quotes in `.env`
- Make sure there are no line breaks in the middle of the key
- Verify the endpoint URL ends with `/openai/v1/` or similar

**Problem: "Model not found" or deployment errors**

- Confirm `OPENAI_DEPLOYMENT` matches the model name from your email exactly
- Check for typos (e.g., `gpt-4o` vs `gpt-4-o`)

**Problem: Rate limiting or quota errors**

- Contact the workshop proctors - the shared API key may have hit its limit
- Wait a minute and try again

**Problem: `uv: command not found`**

```bash
# UV not in PATH - restart your terminal after installation
# Or reinstall:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Then restart your terminal
```

**Problem: `uv sync` fails with dependency conflicts**

```bash
# Clear UV cache and retry:
uv cache clean
uv sync

# If still failing, check your Python version:
python --version  # Should be 3.12+
```

**Problem: Script runs but agent doesn't respond or hangs**

- Check for API key issues (see above)
- Look for error messages in the terminal
- Verify network simulator is responding: `curl http://localhost:8003/health`
- Check you're not hitting rate limits

**Problem: Import errors for `network_simulator_client`**

```bash
# The client is installed as a local package
# Make sure you ran uv sync in the workshop directory:
cd workshop
source .venv/bin/activate
uv sync
```

**Still stuck?**

Ask a workshop proctor for help! In the meantime, these suggestions may be helpful.

1. Double check any error traces
2. Check both terminal windows (network simulator and workshop)
3. Try restarting the network simulator
4. Verify all 4 environment variables are set in `.env`
5. Run `python ex0_verify_setup.py` again to identify what's broken

---

## Part 1: Build Your First Agent

In this exercise, you'll create a simple conversational agent to understand the basic structure of agents in the OpenAI Agents SDK. An agent combines a language model with instructions (the system prompt) that guide its behavior. This foundational pattern appears in every agent you'll build.

### Exercise 1: Hello World Agent

**File:** `workshop/ex1_hello_world.py`

**What you'll do:**

1. Write a system prompt that defines your agent's personality and behavior
2. Give your agent a name
3. Run the agent and have a conversation with it

### Understanding the Agent Structure

The exercise file provides the infrastructure for a multi-turn conversation loop. Your job is to define the agent's behavior through two key parameters: the system prompt and the agent name.

Here's the core agent definition you'll be editing:

```python
# This is the system prompt - your primary tool for controlling behavior
SYSTEM_PROMPT = """
"""

# The Agent object combines the model with your instructions
hello_world_agent = Agent(
    name="<name>",                    # What the agent calls itself
    instructions=SYSTEM_PROMPT,        # How the agent should behave
    model=OpenAIChatCompletionsModel(  # The LLM that powers the agent
        model=GENERATIVE_MODEL,
        openai_client=llm_client
    ),
)
```

**Breaking this down:**

- **`Agent(...)`**: The core SDK class that creates an agent. Every agent you build uses this.
- **`name`**: Gives the agent an identity. This appears in logs and can influence behavior.
- **`instructions`**: The system prompt that defines the agent's role, knowledge, and behavior patterns.
- **`model`**: Specifies which LLM to use. The same instructions with different models can produce different behaviors.

The agent doesn't have tools yet. It can only converse based on what the underlying model knows and what you tell it in the system prompt. Internally, it still runs the agentic loop, but with no tools, that loop only has one iteration...

**Instructions:**

Open `ex1_hello_world.py` and find the `BEGIN EDIT ZONE` (around line 18):

1. **Write a system prompt** (lines 24-25): This is where you define personality and behavior. Consider:

   ```python
   SYSTEM_PROMPT = """
   You are a helpful network engineer who explains complex concepts simply.
   You're enthusiastic about teaching and use analogies to make things clear.
   Keep responses concise but friendly.
   """
   ```

   Or get creative—make it a sarcastic joke-generator, a formal documentation bot, or a poet bot.

2. **Set the agent name** (line 32): Replace `<name>` with something that matches your prompt
   ```python
   name="ChatBot",  # or "SarcasticBot", "JokeBot", etc.
   ```

**Run it:**

```bash
cd workshop
source .venv/bin/activate
python ex1_hello_world.py
```

**Try these interactions:**

- Ask it questions about networking
- Test if it follows the personality you defined
- Type `"""` on a new line for multi-line input
- Type `exit` or `quit` to stop

**Highlight:** System prompts are your primary tool for controlling agent behavior. The same underlying model can become wildly different agents based solely on the instructions you provide. This is the foundation of "prompt engineering."

---

## Part 2: Tools and Function Calling

Agents become powerful when they can take actions, combining intelligence with agency. Tools are pre-written code that agents can call to fetch data, perform calculations, or interact with external systems. When using the OpenAI Agents SDK, the `@function_tool` decorator exposes functions to the agent, and the docstring tells the agent when and how to use them.

### Exercise 2: Node Finder Agent

**File:** `workshop/ex2_node_finder_agent.py`

**What you'll do:**

1. Write a tool that finds network nodes by location.
2. Document that tool.
3. Write a system prompt for an agent that helps users query network topology
4. Test the agent with geographic queries

### Understanding Tools

Here's how [tools](https://openai.github.io/openai-agents-python/tools/) work in the OpenAI Agents SDK. Look at the function structure:

```python
@function_tool
async def get_nodes_by_location(
    latitude: float, longitude: float, max_distance_km: float
) -> str:
    """
    Find network nodes within a specified distance from a geographic point.

    Use this tool to find nodes in a specific geographic region. Useful for
    finding nearby nodes when planning routes or analyzing regional coverage.

    Args:
        latitude: Center point latitude in degrees (-90 to 90)
        longitude: Center point longitude in degrees (-180 to 180)
        max_distance_km: Maximum search radius in kilometers from the center point

    Returns:
        JSON string containing:
        - center_latitude: The search center latitude
        - center_longitude: The search center longitude
        - radius_km: The search radius
        - node_count: Number of nodes found
        - nodes: List of nodes with details including calculated distance_km from center

    Example:
        latitude = 40.7128, longitude = -74.0060, max_distance_km = 100.0
        Finds all nodes within 100km of New York City coordinates
    """
    client = NetworkSimulatorClient()  # Uses BACKEND_URL from environment

    try:
        nodes = client.get_nodes(
            latitude=latitude, longitude=longitude, max_distance_km=max_distance_km
        )

        result_nodes = []
        for node in nodes:
            # Calculate distance using haversine (approximation for display)

            lat1, lon1 = radians(latitude), radians(longitude)
            lat2, lon2 = radians(node.latitude), radians(node.longitude)

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance_km = 6371.0 * c  # Earth's radius in km

            result_nodes.append(
                {
                    "uuid": node.uuid,
                    "name": node.name,
                    "latitude": node.latitude,
                    "longitude": node.longitude,
                    "vendor": node.vendor,
                    "capacity_gbps": node.capacity_gbps,
                    "free_capacity_gbps": node.free_capacity_gbps,
                    "distance_km": round(distance_km, 2),
                }
            )

        return json.dumps(
            {
                "center_latitude": latitude,
                "center_longitude": longitude,
                "radius_km": max_distance_km,
                "node_count": len(result_nodes),
                "nodes": result_nodes,
            }
        )

    except Exception as e:
        return json.dumps(
            {
                "error": str(e),
                "center_latitude": latitude,
                "center_longitude": longitude,
                "radius_km": max_distance_km,
            }
        )
    finally:
        client.close()
```

**Breaking this down:**

- **`@function_tool`**: This decorator tells the SDK "this function is available to the agent." Without it, the function is just regular Python code the agent can't access.
- **Type hints** (`latitude: float`): These are critical! They tell the agent what data types to use when calling the tool.
- **Docstring**: This is the agent's instruction manual for the tool. The agent reads this to decide when and how to use the tool.
- **Return value** (`-> str`): All tool results are serialized into strings. Use `json.dumps()` for structured data.
- **Error handling**: Always include try/except. Tools should gracefully handle failures and return informative errors.

Now look at how the tool is added to the agent:

```python
node_finder_agent = Agent(
    name="<Agent_Name>",
    instructions=SYSTEM_PROMPT,
    model=OpenAIResponsesModel(model=GENERATIVE_MODEL, openai_client=llm_client),
    tools=[get_nodes_by_location],  # This makes the tool available to the agent
    model_settings=ModelSettings(reasoning=None),  # Control model reasoning level
)
```

When the agent receives a user message, it can now:

1. Decide whether to use the tool or just respond directly
2. Extract the required parameters from the user's message
3. Call the tool with those parameters
4. Incorporate the tool's response into its reply to the user

This is the agentic loop in action. The model reasons about what action to take, executes tools if needed, and uses the results to formulate responses.

**Instructions:**

Your task is to document the tool so the agent understands when and how to use it:

1. **Write the tool docstring**: The agent will read this to decide when to call the tool. Here is an example:

   ```python
   """
   Finds network nodes within a geographic radius.

   Args:
       latitude: Center point latitude in decimal degrees
       longitude: Center point longitude in decimal degrees
       max_distance_km: Search radius in kilometers

   Returns:
       JSON with node details including name, location, capacity, and distance

   Use this when users ask to find nodes near a location, within a radius,
   or in a geographic area. Users may provide city names or coordinates.
   """
   ```

2. **Write a system prompt**: Guide the agent's overall behavior:

   ```python
   SYSTEM_PROMPT = """
   You help users find network nodes by geographic location.
   When users mention cities or locations, use the get_nodes_by_location tool.
   Present results in a clear, organized format showing node names and distances.
   """
   ```

3. **Set the agent name**

**Run it:**

```bash
python ex2_node_finder_agent.py
```

**Test queries:**

- "Find nodes near New York, New York? (40.7128° N, 74.0060° W)"
- "What nodes are within 50km of coordinates 40.4387, 79.9972?"
- "Show me network equipment near Denver"
- "{"dist": "20km", "lat": 39.9526, "lon": 75.1652}"

**Highlight:** Tool documentation is critical. The agent only knows what you tell it in the docstring. The agent uses:

1. **Function name** for context (clear names help)
2. **Type hints** to understand what data to pass
3. **Docstring** to decide when and why to call the tool
4. **System prompt** for overall guidance on tool usage

This layered approach—function implementation, clear documentation, and system prompt guidance—is how you build reliable agentic systems.

---

## Part 3: Multi-Tool Planning

When agents have access to multiple tools, they must decide which tools to use and in what order. This exercise introduces an agent with seven different tools for querying network topology, checking services, and planning routes. Quality tool documentation and a well-crafted system prompt become essential for guiding these decisions.

### Exercise 3: Planning Agent

**File:** `workshop/ex3_planning_agent.py`

**What you'll do:**

1. Document seven network query tools
2. Write a system prompt that helps the agent orchestrate these tools effectively
3. Test complex, multi-step queries

### Understanding Multi-Tool Orchestration

With multiple tools, the agent must decide which tool to use and when. Look at how the planning agent is configured:

```python
planning_agent = Agent(
    name="NetworkPlanningAgent",
    instructions="""
    TODO: Write a system prompt
    """,
    model=OpenAIResponsesModel(model=GENERATIVE_MODEL, openai_client=llm_client),
    tools=[
        get_nodes_by_name,        # Search by name
        get_nodes_by_location,    # Search by geography
        get_node_by_uuid,         # Get specific node details
        get_edge_by_uuid,         # Get specific edge details
        get_edge_by_endpoints,    # Find edge between two nodes
        get_node_services,        # List services on a node
        find_and_plan_route,      # Plan capacity-aware routes
    ],
    model_settings=ModelSettings(reasoning=None),
)
```

The agent now has seven different capabilities. When a user asks a question, the agent must:

1. **Understand the intent**: What is the user asking for?
2. **Select relevant tools**: Which tools can help answer this?
3. **Determine order**: Should I call tools sequentially or is one enough?
4. **Combine results**: How do I synthesize multiple tool outputs into a coherent answer?

This is where tool documentation and system prompts become critical. The agent reads your docstrings to understand each tool's purpose, then uses the system prompt for high-level guidance on orchestration.

### Example Tool Flow

Consider the query: "Plan a route from Austin to Dallas with at least 10 Gbps capacity"

The agent might:

1. Call `get_nodes_by_location()` twice to find nodes in NYC and Washington, DC
2. Pick specific start/end nodes from those results
3. Call `find_and_plan_route()` with those nodes and the capacity requirement
4. Optionally call `get_edge_by_uuid()` to get details about edges in the planned route
5. Present the complete route plan to the user

The agent figures out this sequence by reading your tool documentation and following your system prompt guidance.

**Instructions:**

Seven tools are implemented but need documentation. Find the `BEGIN EDIT ZONE` markers for each:

1. **`get_nodes_by_name()`** (lines 33-35): Search nodes by name substring
   Document: what substring matching does, what gets returned

2. **`get_nodes_by_location()`** (lines 68-70): Find nodes within geographic radius
   Document: how to specify center point and radius, what distance calculation is used

3. **`get_node_services()`** (lines 130-132): List services running on a node
   Document: what a "service" is (network service like MPLS, BGP), what details are provided

4. **`get_edge_by_uuid()`** (lines 176-178): Get edge details by ID
   Document: when you'd look up an edge by UUID vs other methods

5. **`get_edge_by_endpoints()`** (lines 203-205): Find edge between two nodes
   Document: difference from get_edge_by_uuid, what happens if no edge exists

6. **`get_node_by_uuid()`** (lines 235-237): Get detailed node information
   Document: comprehensive node details vs summary info from search tools

7. **`find_and_plan_route()`** (lines 268-270): Plan routes with capacity constraints
   Document: how capacity checking works, what makes a valid route, failure cases

For each, explain:

- What the tool does
- When to use it vs alternatives
- What the return format looks like
- Any constraints or edge cases

8. **Write the system prompt** (lines 320-322): Guide multi-tool orchestration:

   ```python
   """
   You are a network planning assistant that helps users query and analyze network topology.

   Available capabilities:
   - Search for nodes by name or location
   - Get detailed information about specific nodes and edges
   - Check what services are running on nodes
   - Plan routes between nodes with capacity requirements

   When users ask complex questions, break them down into steps:
   1. First, find the relevant nodes (by name or location)
   2. Then, get details or plan routes as needed
   3. Present results in a clear, organized format

   Always explain your reasoning when planning routes or making recommendations.
   """
   ```

**Run it:**

```bash
python ex3_planning_agent.py
```

**Test scenarios that require multiple tools:**

- "Find nodes with 'ALB' in the name in NYC" → location search + filtering
- "What services are running on node X?" → node lookup + service query
- "Plan a route from node A to node B with at least 5 Gbps capacity" → node lookups + route planning
- "Show me all edges connected to Denver nodes" → location search + edge queries

**What you're learning:** With multiple tools, agent behavior depends on three layers:

1. **Tool names**: Clear, descriptive names help the agent choose correctly
2. **Tool docstrings**: Detailed documentation guides when and how to use each tool
3. **System prompt**: High-level orchestration guidance helps the agent combine tools effectively

Watch how the agent chains tools together. Poor documentation leads to wrong tool selection or unnecessary tool calls. Good documentation enables efficient, accurate multi-step reasoning.

---

## Part 4: Inter-Agent Architecture

Real-world agentic systems often involve multiple specialized agents working together. This exercise introduces a provisioning agent with write capabilities—it can create and delete network resources. You'll see how to build agents that modify state safely, enforce constraints, and coordinate with other agents (like the planning agent from Exercise 3).

### Exercise 4: Provisioning Agent

**File:** `workshop/ex4_provisioning_agent.py`

**What you'll do:**

1. Document five provisioning tools that modify network state
2. Write a system prompt that ensures safe, constraint-aware provisioning
3. Use the planning agent to generate routes, then provision them with this agent

### Understanding State-Modifying Agents

Until now, all tools have been read-only—they query data but don't change anything. The provisioning agent is different:

```python
provisioning_agent = Agent(
    name="NetworkProvisioningAgent",
    instructions="""
    TODO: Write a system prompt
    """,
    model=OpenAIResponsesModel(model=GENERATIVE_MODEL, openai_client=llm_client),
    tools=[
        create_edge,         # WRITES: Adds network capacity
        delete_edge,         # WRITES: Removes edges
        create_service,      # WRITES: Provisions services
        delete_service,      # WRITES: Removes services
        get_database_stats,  # READ: Query Database for Aggregate stats
    ],
    model_settings=ModelSettings(reasoning=None),
)
```

These tools modify the network database. This introduces new challenges:

- **Irreversibility**: Deleting something can't always be undone
- **Constraints**: Some operations have prerequisites (e.g., can't create new edges without an existing connection)
- **Validation**: The agent must understand and respect business rules
- **Error handling**: Failed operations need clear, actionable error messages

### Example: Constraint Enforcement in Tools

Look at how `create_edge()` enforces constraints:

```python
@function_tool
async def create_edge(
    source_node_uuid: str,
    target_node_uuid: str,
    capacity_gbps: int,
    latency_ms: float
) -> str:
    """
    TODO: Document this tool
    """
    client = NetworkSimulatorClient()

    try:
        # Check if an edge already exists between these nodes
        existing_edges = client.get_edges(
            source_node_uuid=source_node_uuid,
            target_node_uuid=target_node_uuid
        )

        if not existing_edges:
            # CONSTRAINT: Can only create parallel edges
            return json.dumps({
                "error": "Cannot create edge: no existing connection found",
                "detail": "This tool only adds parallel capacity. Create initial connection first.",
                "source_node_uuid": source_node_uuid,
                "target_node_uuid": target_node_uuid,
            })

        # Create the parallel edge
        new_edge = client.create_edge(
            source_node_uuid=source_node_uuid,
            target_node_uuid=target_node_uuid,
            capacity_gbps=capacity_gbps,
            latency_ms=latency_ms,
        )

        return json.dumps({
            "success": True,
            "edge_uuid": new_edge.uuid,
            "capacity_gbps": capacity_gbps,
            "message": "Parallel edge created successfully"
        })

    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        client.close()
```

The tool itself enforces the constraint—the agent can't bypass it. The error message guides the agent toward correct behavior.

### Multi-Agent Workflow Pattern

The planning and provisioning agents work together:

1. **Planning Agent** (Exercise 3):

   - Read-only operations
   - Explores possibilities
   - Finds optimal routes
   - Output: Detailed plan (Take note of exactly what information the Provisioning Agent needs!)

2. **Provisioning Agent** (Exercise 4):
   - Write operations
   - Implements plans
   - Enforces constraints
   - Output: Provisioned resources

This separation mirrors real-world roles...

This is the "division of labor" pattern—specialized agents with clear boundaries.

**Instructions:**

Five provisioning tools need documentation:

1. **`create_edge()`** (lines 29-31): Add parallel capacity to existing connections
   Document: the parallel-only constraint, what parameters are needed, success/failure formats

2. **`delete_edge()`** (lines 90-92): Remove network edges
   Document: what happens to services using this edge, irreversibility warning

3. **`create_service()`** (lines 121-123): Provision services with specific paths
   Document: what a path is (list of edge UUIDs), capacity requirements, when this fails

4. **`delete_service()`** (lines 170-172): Remove services
   Document: clean deletion process, what gets freed up

5. **`get_database_stats()`** (lines 195-197): Query network statistics
   Document: what stats are available, when to check state before/after modifications

For each, emphasize:

- What constraints exist
- What error messages mean
- How to handle failures gracefully

6. **Write the system prompt** (lines 221-223): Ensure safe provisioning:

   ```python
   """
   You are a network provisioning agent that implements network changes.

   IMPORTANT CONSTRAINTS:
   - You can only create PARALLEL edges (additional capacity on existing connections)
   - You cannot create initial connections between nodes
   - Services require a valid path (list of edge UUIDs with sufficient capacity)
   - Always check database stats before and after major changes

   Workflow:
   1. Understand the provisioning request
   2. Validate that it's possible given constraints
   3. Execute changes in the correct order (edges first, then services)
   4. Confirm success and report what was created

   If a tool returns an error, explain what went wrong and what would need to
   change for the operation to succeed.
   """
   ```

**Run it:**

```bash
python ex4_provisioning_agent.py
```

**Workflow to test the multi-agent pattern:**

1. Run the planning agent (Exercise 3): `python ex3_planning_agent.py`
2. Ask: "Plan a route from Dover, DE to Lansing, MI with 1 Gbps capacity"
3. Copy the route plan it generates (including edge UUIDs and capacities)
4. Run the provisioning agent: `python ex4_provisioning_agent.py`
5. Paste the route plan and ask it to provision
6. Watch it create edges and services step-by-step

**Highlight:** State-modifying agents require careful design at multiple levels:

- **Tool level**: Enforce constraints in code, return informative errors
- **Documentation level**: Explain constraints clearly so the agent understands them
- **System prompt level**: Guide the agent toward safe, valid operation sequences

Multi-agent architectures let you separate concerns:

- **Read-only agents** explore possibilities without risk
- **Write agents** execute with safeguards and validation
- **Handoffs** use structured data to coordinate

This pattern scales to production systems—specialized agents with clear responsibilities and constrained capabilities are easier to test, maintain, and trust than monolithic agents that do everything.

---

## Summary and Next Steps

You've built four progressively complex agents:

1. A conversational agent controlled by system prompts
2. A single-tool agent that queries network topology
3. A multi-tool agent that orchestrates complex queries
4. A provisioning agent that modifies network state

These patterns scale to production systems. The key principles remain the same:

- Clear system prompts guide agent behavior
- Well-documented tools enable correct decision-making
- Multiple specialized agents often outperform a single general-purpose one

**To continue exploring:**

- Experiment with different system prompts and observe behavior changes
- Add new tools to existing agents, you can find additional API helper functions in `workshop/network_simulator_client`
- Chain between the Planning and Provisioning agents using [handoffs](https://openai.github.io/openai-agents-python/handoffs/) automatically, rather than copy-paste.

The code and network simulator remain available for you to experiment with after the workshop. API keys will be deactivated after the conclusion of the workshop.
