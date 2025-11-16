#!/usr/bin/env python3
"""
Excercise 1 - Building Your First Agent
This is a reference solution, you CANNOT run this file from the solutions directory...
"""
import asyncio
import textwrap
from colorama import Fore, Style, init as colorama_init
from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled, Runner
from dotenv import load_dotenv
from config import llm_client, GENERATIVE_MODEL

# Load environment variables
load_dotenv()

# ================================================================
# ===                     BEGIN EDIT ZONE                     ===
# ===  Participants: modify the code between these markers.   ===
# ================================================================

# This is the system prompt.
# It allows us to guide the agent's behavior, provide context about the problem space, and recommend solution paths.
# It is also an integral part of establishing acceptable language, tone, and response formats.

SYSTEM_PROMPT = """
You are a kind, friendly, and charming conversationalist. 
Respond to the user in a way that allows for an engaging conversation.

Be sure to begin each reply with the phrase "Hello World!"
"""

# Try to editing the prompt above in creative and unique ways.
# In this example, all that the agent knows is within the underlying model's knowledge space and the prompt above.
# Perhaps you can give the agent a new name, give it some knowledge on a specific topic, or change the format with which it responds to you...

hello_world_agent = Agent(
    name="ConversationalAgent",
    instructions=SYSTEM_PROMPT,
    model=OpenAIChatCompletionsModel(model=GENERATIVE_MODEL, openai_client=llm_client),
)

# ================================================================
# ===                      END EDIT ZONE                      ===
# ===      Do not modify anything beyond this point.          ===
# ================================================================


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
                result = await Runner.run(hello_world_agent, user_input)
            else:
                # Append new user message to history in proper format
                new_input = conversation_history + [
                    {"role": "user", "content": user_input}
                ]
                result = await Runner.run(hello_world_agent, new_input)

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
