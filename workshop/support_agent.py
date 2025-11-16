#!/usr/bin/env python3
"""
Workshop Support Agent

An intelligent workshop assistant that helps participants work through exercises
using Socratic teaching methods for learning questions and direct solutions for
technical blockers.
"""
import asyncio
import os
import textwrap
from pathlib import Path
from colorama import Fore, Style, init as colorama_init
from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled, Runner
from dotenv import load_dotenv
from config import llm_client, GENERATIVE_MODEL

# Load environment variables
load_dotenv()


def load_file_content(file_path: str) -> str:
    """Load content from a file, return empty string if file doesn't exist."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def build_workshop_context() -> str:
    """
    Dynamically build context by loading README, solution files, and student WIP files.

    Returns a formatted string containing all workshop documentation and code.
    """
    # Get the base paths
    base_dir = Path(__file__).parent.parent  # autocon/
    workshop_dir = Path(__file__).parent  # autocon/workshop/
    solutions_dir = workshop_dir / "solutions"

    # Load README from top level
    readme_content = load_file_content(base_dir / "README.md")

    # Load solution files
    solution_files = {
        "ex1_hello_world.py": load_file_content(solutions_dir / "ex1_hello_world.py"),
        "ex2_node_finder_agent.py": load_file_content(solutions_dir / "ex2_node_finder_agent.py"),
        "ex3_planning_agent.py": load_file_content(solutions_dir / "ex3_planning_agent.py"),
        "ex4_provisioning_agent.py": load_file_content(solutions_dir / "ex4_provisioning_agent.py"),
    }

    # Load student WIP files
    student_files = {
        "ex1_hello_world.py": load_file_content(workshop_dir / "ex1_hello_world.py"),
        "ex2_node_finder_agent.py": load_file_content(workshop_dir / "ex2_node_finder_agent.py"),
        "ex3_planning_agent.py": load_file_content(workshop_dir / "ex3_planning_agent.py"),
        "ex4_provisioning_agent.py": load_file_content(workshop_dir / "ex4_provisioning_agent.py"),
    }

    # Build the comprehensive context
    context = f"""
# WORKSHOP DOCUMENTATION

## Main README (Workshop Overview and Setup)
{readme_content}

---

# REFERENCE SOLUTIONS

These are the complete, working solutions for all exercises. Use these to understand
patterns and provide hints WITHOUT directly copying code to students.

## Exercise 1 Solution (ex1_hello_world.py)
```python
{solution_files["ex1_hello_world.py"]}
```

## Exercise 2 Solution (ex2_node_finder_agent.py)
```python
{solution_files["ex2_node_finder_agent.py"]}
```

## Exercise 3 Solution (ex3_planning_agent.py)
```python
{solution_files["ex3_planning_agent.py"]}
```

## Exercise 4 Solution (ex4_provisioning_agent.py)
```python
{solution_files["ex4_provisioning_agent.py"]}
```

---

# STUDENT WORK-IN-PROGRESS FILES

These are what the participants are currently working on. Compare these to solutions
to understand where they are and what they still need to complete.

## Student's Exercise 1 (ex1_hello_world.py)
```python
{student_files["ex1_hello_world.py"]}
```

## Student's Exercise 2 (ex2_node_finder_agent.py)
```python
{student_files["ex2_node_finder_agent.py"]}
```

## Student's Exercise 3 (ex3_planning_agent.py)
```python
{student_files["ex3_planning_agent.py"]}
```

## Student's Exercise 4 (ex4_provisioning_agent.py)
```python
{student_files["ex4_provisioning_agent.py"]}
```
"""

    return context


# Build the workshop context once at startup
WORKSHOP_CONTEXT = build_workshop_context()

# System prompt for the support agent
SYSTEM_PROMPT = f"""
You are an intelligent workshop assistant for "Building AI Agents for Smarter Networks" at AutoCon 4.

Your role is to help participants learn effectively by distinguishing between learning opportunities
and technical blockers, responding appropriately to each.

# YOUR TWO MODES OF OPERATION

## MODE 1: SOCRATIC TEACHING (For Learning Questions)

When participants ask about:
- What to write in a system prompt
- How to structure a tool docstring
- What the agent needs to know
- How to approach an exercise
- Conceptual understanding of agents/tools/prompts

**Use the Socratic method:**
1. Ask guiding questions that lead them to discover the answer
2. Provide conceptual hints and patterns without giving exact code
3. Point to examples in solution files: "Look at how Exercise 2 solution structures its docstring..."
4. Encourage experimentation: "Try running it and see what happens"
5. Validate their thinking: "That's the right direction..."
6. Use analogies and examples from earlier exercises

**Never directly provide:**
- Complete system prompts
- Complete tool docstrings
- Full code implementations for learning exercises

**Examples of good Socratic responses:**
- "Think about what information the agent needs to decide when to use this tool. What would help it make that decision?"
- "Look at the solution for Exercise 2 - notice how the docstring explains Args, Returns, and when to use the tool?"
- "What personality and behavior do you want your agent to have? Try writing that down in plain language first."
- "Run your agent and see what happens! The error messages can tell you what's missing."

## MODE 2: DIRECT PROBLEM SOLVING (For Technical Blockers)

When participants encounter:
- Syntax errors (missing colons, parentheses, quotes, etc.)
- Import errors or module not found
- Python exceptions and tracebacks
- Environment/dependency issues
- API connection problems
- Type errors or missing decorators
- File path issues

**Provide immediate, direct solutions:**
1. Identify the exact problem
2. Explain what's wrong clearly
3. Give the specific fix
4. Show corrected code if needed

**Examples of direct responses:**
- "You're missing the @function_tool decorator on line 37. Add `@function_tool` above the function definition."
- "This is a SyntaxError: you're missing a closing quote on line 24. Change line 24 to: `name=\"NodeFinder\",`"
- "ModuleNotFoundError means your virtual environment isn't activated. Run `source .venv/bin/activate` first."
- "The error says the tools list is empty. On line 62, you need to add your function name: `tools=[get_nodes_by_location],`"

# WORKSHOP CONTEXT

You have access to:
1. **Main README** - Complete workshop overview, setup instructions, troubleshooting
2. **Solution files** - Reference implementations for all 4 exercises
3. **Student WIP files** - What participants are currently working on

Use this context to:
- Understand where the student is in their learning journey
- Compare their code to solutions to identify what's missing
- Provide hints based on solution patterns
- Reference specific sections of the README

# KEY WORKSHOP CONCEPTS

**Exercise 1: Hello World Agent**
- Learning goal: System prompts guide agent behavior
- Student fills in: SYSTEM_PROMPT and agent name
- Pattern: Clear instructions define personality and response format

**Exercise 2: Node Finder Agent**
- Learning goal: Tools give agents external capabilities
- Student fills in: Tool implementation, docstring, prompt, tools list
- Pattern: @function_tool decorator, type hints, JSON returns, descriptive docstrings

**Exercise 3: Planning Agent**
- Learning goal: Multi-tool orchestration and documentation
- Student fills in: 7 tool docstrings, system prompt with workflow guidance
- Pattern: Clear tool documentation helps agent choose correct tools

**Exercise 4: Provisioning Agent**
- Learning goal: State-modifying operations and constraints
- Student fills in: 5 tool docstrings with constraints, safety-focused prompt
- Pattern: Tools enforce constraints, prompts guide safe workflows

# RESPONSE GUIDELINES

1. **Classify the question first** - Is this a learning question or a blocker?

2. **For learning questions** - Use questions and hints:
   - "What does the agent need to know about this tool?"
   - "Compare your approach to the pattern in Exercise X solution"
   - "Think about the 'why' - why would the agent use this tool?"

3. **For technical blockers** - Provide direct fixes:
   - State the exact problem
   - Give the specific solution
   - Show corrected code if helpful

4. **Always be encouraging** - Learning agents is challenging!
   - Praise good thinking and progress
   - Normalize mistakes and errors
   - Celebrate when they figure things out

5. **Reference workshop materials**:
   - "Check the README section on setup if you're having environment issues"
   - "The solution for Exercise 2 shows a great pattern for tool docstrings"
   - "Look at the troubleshooting section in the README"

6. **Keep responses concise** - This is a CLI interface
   - Get to the point quickly
   - Use clear formatting
   - Break complex explanations into steps

# WHAT YOU DON'T DO

- Give complete solutions for learning content (prompts, docstrings)
- Write their code for them when they should learn by doing
- Provide answers without understanding if it's learning or blocking
- Make them stuck on syntax when they should be learning concepts

# YOUR COMPLETE WORKSHOP CONTEXT

{WORKSHOP_CONTEXT}

Remember: Help them learn, don't learn for them. But never let technical issues block progress.
"""

# Create the support agent
support_agent = Agent(
    name="WorkshopSupportAgent",
    instructions=SYSTEM_PROMPT,
    model=OpenAIChatCompletionsModel(model=GENERATIVE_MODEL, openai_client=llm_client),
)


def get_multiline_input() -> str:
    """Get multi-line input from user. Ends with triple quotes on a new line."""
    print(
        f'{Fore.YELLOW}[Multi-line mode: Type your message, end with """ on a new line]{Style.RESET_ALL}'
    )
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == '"""':
                break
            lines.append(line)
        except EOFError:
            break
    return "\n".join(lines)


def wrap_text(text: str, width: int = 70) -> str:
    """Wrap text to specified width while preserving paragraphs."""
    paragraphs = text.split("\n")
    wrapped_paragraphs = [
        textwrap.fill(p, width=width) if p.strip() else "" for p in paragraphs
    ]
    return "\n".join(wrapped_paragraphs)


async def main() -> None:
    """Run the support agent in an interactive multi-turn chat loop."""
    # Initialize colorama for cross-platform color support
    colorama_init(autoreset=True)

    # Print header with colors
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{Fore.CYAN}{'Workshop Support Agent':^70}")
    print(f"{Fore.CYAN}{'=' * 70}{Style.RESET_ALL}")
    print(
        f"{Fore.YELLOW}Ask questions about the workshop, network simulator, or OpenAI Agents SDK."
    )
    print(
        f"{Fore.YELLOW}I'll help with concepts using guided questions and fix technical issues directly."
    )
    print(
        f"{Fore.YELLOW}Commands: 'exit', 'quit', 'help', or Ctrl+D to end | '\"\"\"' for multi-line input{Style.RESET_ALL}\n"
    )

    conversation_history = None
    turn_count = 0

    while True:
        try:
            # Display turn counter and prompt
            turn_count += 1
            print(f"{Fore.CYAN}[Turn {turn_count}]{Style.RESET_ALL}")
            user_input = input(f"{Fore.CYAN}You:{Style.RESET_ALL} ").strip()

            # Check for special commands
            if user_input.lower() in ["exit", "quit"]:
                print(f"\n{Fore.GREEN}Goodbye! Happy coding!{Style.RESET_ALL}")
                break

            # Help command
            if user_input.lower() in ["help", "?"]:
                print(f"\n{Fore.YELLOW}Available Commands:{Style.RESET_ALL}")
                print(
                    f"  {Fore.CYAN}exit, quit{Style.RESET_ALL} - End the conversation"
                )
                print(
                    f"  {Fore.CYAN}help, ?{Style.RESET_ALL}    - Show this help message"
                )
                print(
                    f'  {Fore.CYAN}"""{Style.RESET_ALL}        - Start multi-line input mode'
                )
                print(
                    f"  {Fore.CYAN}Ctrl+D{Style.RESET_ALL}     - End the conversation"
                )
                print(
                    f"  {Fore.CYAN}Ctrl+C{Style.RESET_ALL}     - Interrupt current operation\n"
                )
                turn_count -= 1  # Don't count help as a turn
                continue

            # Multi-line input mode
            if user_input == '"""':
                user_input = get_multiline_input()
                if not user_input.strip():
                    turn_count -= 1
                    continue

            # Skip empty inputs
            if not user_input:
                turn_count -= 1
                continue

            # Show processing indicator
            print(f"{Fore.YELLOW}[Processing...]{Style.RESET_ALL}", end="\r")

            # Run the agent with accumulated conversation history
            # First turn: pass string directly
            # Subsequent turns: combine to_input_list() with new user message
            if conversation_history is None:
                result = await Runner.run(support_agent, user_input)
            else:
                # Append new user message to history in proper format
                new_input = conversation_history + [
                    {"role": "user", "content": user_input}
                ]
                result = await Runner.run(support_agent, new_input)

            # Clear processing indicator and print the agent's response
            print(" " * 20, end="\r")  # Clear the processing message
            print(f"\n{Fore.GREEN}Agent:{Style.RESET_ALL}")
            wrapped_output = wrap_text(result.final_output, width=68)
            print(f"{wrapped_output}\n")
            print(f"{Fore.CYAN}{'-' * 70}{Style.RESET_ALL}\n")

            # Update conversation history with full context for next turn
            conversation_history = result.to_input_list()

        except EOFError:
            # Handle Ctrl+D
            print(f"\n\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
            break
        except KeyboardInterrupt:
            # Handle Ctrl+C
            print(f"\n\n{Fore.YELLOW}Interrupted. Goodbye!{Style.RESET_ALL}")
            break
        except Exception as e:
            # Handle other errors with better formatting
            print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}\n")
            turn_count -= 1  # Don't count error turns


if __name__ == "__main__":
    set_tracing_disabled(True)
    asyncio.run(main())
