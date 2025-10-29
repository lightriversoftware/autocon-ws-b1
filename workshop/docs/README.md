# AI Agents for Network Management - Workshop

Learn to build intelligent network agents using the OpenAI Agents SDK.

## Quick Start

1. **Setup**: Follow [SETUP.md](SETUP.md)
2. **Start Building**: See [EXERCISE_GUIDE.md](EXERCISE_GUIDE.md)
3. **API Reference**: [NETWORK_REFERENCE.md](NETWORK_REFERENCE.md)

## Workshop Goals

- Learn to segment agent responsibilities effectively
- Master prompt engineering for agentic workflows
- Build agents that use tools to manage network infrastructure
- Design multi-agent systems

## What You'll Build

1. **Support Agent** - Conversational help without tools
2. **Planning Agent** - Route finding with capacity validation
3. **Provisioning Agent** - Service creation on network paths

## Files

```
workshop/
├── ex1_support_agent.py          # Example: working support agent
├── ex2_planning_agent.py         # Your code: planning agent
├── ex3_provisioning_agent.py     # Your code: provisioning agent
├── ex0_verify_setup.py           # Setup verification
└── solutions/                    # Reference implementations
```

## Documentation

- **SETUP.md** - Installation & configuration
- **EXERCISE_GUIDE.md** - Workshop exercises
- **NETWORK_REFERENCE.md** - API reference

## Common Issues

| Problem | Solution |
|---------|----------|
| API connection fails | Start simulator with uvicorn (see SETUP.md) |
| No API key | Create `.env` with Azure OpenAI credentials |
| Import errors | Run `uv sync` in workshop directory |
| Agent won't call tools | Improve tool docstrings |

## Resources

- **OpenAI Agents SDK**: https://openai.github.io/openai-agents-python/
- **Network API Docs**: http://localhost:8003/docs (when simulator running)
