# Exercise Guide

## Workshop Goal

Learn to build effective AI agents through:
- Good tool design and documentation
- Clear agent system prompts
- Proper segmentation of responsibilities

## Files Overview

- `ex0_verify_setup.py` - Verify your environment works
- `ex1_support_agent.py` - Complete example (study this!)
- `ex2_planning_agent.py` - Planning agent with TODO docstrings
- `ex3_provisioning_agent.py` - Provisioning agent with TODO docstrings
- `solutions/` - Reference implementations

## Exercise 1: Understanding Agent Design

**Goal**: Study the working support agent to understand agent design patterns.

**Tasks**:
1. Open `ex1_support_agent.py`
2. Examine the agent's system prompt - how does it provide context?
3. Note what the agent does WITHOUT tools - it uses embedded documentation
4. Run it: `python ex1_support_agent.py`
5. Ask it questions about the network simulator and SDK

**Key Takeaways**:
- Agents don't always need tools - context injection works too
- System prompts guide agent behavior
- Clear role definition helps agents stay focused

## Exercise 2: Build Planning Agent

**Goal**: Make tools useful by writing clear docstrings.

**File**: `ex2_planning_agent.py`

The planning agent finds network routes between nodes. The code is implemented but tool docstrings say "TODO" - agents won't know how to use them!

**Your Task**: Replace each TODO with a clear docstring that tells the agent:
1. What the tool does
2. When to use it
3. What parameters it needs
4. What it returns

**Example of a good tool docstring**:
```python
@function_tool
async def get_nodes_by_name(name_substring: str) -> str:
    """
    Search for network nodes by name (case-insensitive substring match).

    Use this when the user provides a city name instead of a UUID.
    For example, if user asks for "Albany", this finds "Albany-NY".

    Args:
        name_substring: Part of the city name (e.g., "Albany", "Boston", "New York")

    Returns:
        JSON list of matching nodes with uuid, name, capacity, and location.
        Returns empty list if no matches found.

    Example: get_nodes_by_name("Albany") finds nodes like "Albany-NY"
    """
```

**Tools to document**:
- `get_nodes_by_name()` - Search nodes by city name
- `compute_route()` - Find path between two nodes
- `validate_path()` - Check if a path has sufficient capacity

**Test it**: Run `python ex2_planning_agent.py` and ask it to find routes.

**Success Criteria**:
- Agent knows when to call which tool
- Agent handles both city names and UUIDs correctly
- Agent explains routes clearly to users

## Exercise 3: Build Provisioning Agent

**Goal**: Enable service provisioning through clear tool documentation.

**File**: `ex3_provisioning_agent.py`

The provisioning agent creates network services and edges. Again, code exists but docstrings need work.

**Your Task**: Document these tools:
- `create_edge()` - Add/expand network capacity
- `create_service()` - Provision a service on a path
- `get_service()` - Retrieve service details
- `delete_service()` - Remove a service
- `get_edge_utilization()` - Check capacity usage

**Important considerations for docstrings**:
- `create_edge()` can only expand existing connections (document this constraint!)
- `create_service()` requires ALL parameters from the planning agent's output
- Parameter validation - what values are valid?

**Test it**:
1. First use planning agent to get a route
2. Copy that route info
3. Run provisioning agent to create a service

**Success Criteria**:
- Agent correctly interprets planning agent output
- Agent knows it can't create edges where none exist
- Agent validates parameters before calling tools

## Exercise 4: System Prompt Refinement

**Goal**: Improve agent behavior through better instructions.

**Tasks**:

1. **Examine current prompts** in ex2 and ex3
   - What behavior do they specify?
   - What's missing?

2. **Improve the planning agent prompt** to:
   - Explain its role clearly
   - Guide the workflow (search nodes → compute route → present results)
   - Specify output format
   - Handle errors gracefully

3. **Improve the provisioning agent prompt** to:
   - Clarify when to create edges vs services
   - Explain the constraint about existing connections
   - Specify validation steps
   - Define success/failure reporting format

**Questions to consider**:
- How much detail should the system prompt have?
- Should you specify exact steps or let the agent decide?
- How do you balance flexibility with correctness?

## Exercise 5: Multi-Agent Workflow

**Goal**: Use agents together for end-to-end service provisioning.

**Scenario**: User wants to provision a service from "Albany" to "Miami" with 10 Gbps.

**Workflow**:
1. Run planning agent → get feasible route
2. Copy route details
3. Run provisioning agent → create service
4. Verify service exists

**Reflection Questions**:
- How do agents pass information between each other?
- What format works best for inter-agent communication?
- Where could this workflow fail? How would you handle it?
- Could you automate the handoff between agents?

## Key Concepts

### Tool Design
- **Clear purpose**: Each tool does one thing well
- **Good docstrings**: Agent knows when and how to use it
- **Validation**: Check inputs, handle errors gracefully
- **Examples**: Show the agent how to use it

### Agent Segmentation
- **Planning Agent**: Reads network, computes routes (read-only)
- **Provisioning Agent**: Modifies network, creates services (write operations)
- **Support Agent**: Helps users, no network access (information-only)

Why separate?
- Clear responsibilities
- Easier testing
- Safety (planning can't break things)
- Simpler prompts

### Prompt Engineering
- **Role definition**: What is the agent's job?
- **Context**: What does it need to know?
- **Workflow**: What steps should it follow?
- **Constraints**: What should it NOT do?
- **Output format**: How should it present results?

## Going Further

**Ideas to try**:
- Add error recovery to agents
- Build a monitoring agent (track capacity over time)
- Create an orchestrator agent that coordinates planning + provisioning
- Add memory so agents remember previous conversations
- Implement async workflows for parallel operations

**Advanced Topics**:
- Agent handoffs (built into OpenAI Agents SDK)
- Multi-model agents (use different models for different agents)
- Streaming responses
- Agent evaluation and testing

## Resources

- **OpenAI Agents SDK**: https://openai.github.io/openai-agents-python/
- **Network API Docs**: http://localhost:8003/docs (when simulator is running)
- **Network Reference**: [NETWORK_REFERENCE.md](NETWORK_REFERENCE.md)

## Tips

1. **Start simple**: Get basic functionality working first
2. **Test incrementally**: Test each tool individually
3. **Read errors carefully**: They often tell you exactly what's wrong
4. **Study ex1**: The support agent is a complete, working example
5. **Check solutions**: If stuck, compare with `solutions/` directory
6. **Iterate**: First pass won't be perfect - refine based on testing
