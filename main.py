#!/usr/bin/env python3
import os
import sys
import json
import asyncio
from dotenv import load_dotenv
from langsmith.integrations.claude_agent_sdk import configure_claude_agent_sdk
from agent import run_agent


# Load environment variables (override=True to take precedence over shell env vars)
load_dotenv(override=True)

# Setup Claude Agent SDK with LangSmith tracing
configure_claude_agent_sdk()


async def run_traced_agent(user_message: str) -> str:
    """
    Run the agent with LangSmith tracing enabled.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "Error: ANTHROPIC_API_KEY not found in environment"

    return await run_agent(user_message, api_key)


async def main_async():
    """
    Batch run the agent on inputs from a JSON file.
    """
    # Verify environment variables
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not found")
        print("Please create a .env file with your API keys (see .env.example)")
        sys.exit(1)

    # Check LangSmith configuration
    if os.getenv("LANGSMITH_API_KEY") and os.getenv("LANGSMITH_TRACING") == "true":
        project = os.getenv("LANGSMITH_PROJECT", "trip-planner-agent")
        endpoint = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        print(f"LangSmith tracing enabled")
        print(f"  Project: {project}")
        print(f"  Endpoint: {endpoint}")
        print()
    else:
        print("LangSmith tracing not configured")
        print("Set LANGSMITH_API_KEY and LANGSMITH_TRACING=true in .env to enable")
        print()

    # Get input file from command line args
    input_file = sys.argv[1] if len(sys.argv) > 1 else "inputs.json"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        print("Usage: python main.py [inputs.json]")
        print()
        print("Expected JSON format:")
        print('  ["query 1", "query 2", ...]')
        sys.exit(1)

    # Load inputs from JSON file
    with open(input_file, "r") as f:
        inputs = json.load(f)

    if not isinstance(inputs, list):
        print("Error: JSON file should contain a list of input strings")
        sys.exit(1)

    print("=" * 60)
    print("Trip Planner Agent - Batch Mode")
    print("=" * 60)
    print(f"Processing {len(inputs)} inputs from {input_file}")
    print()

    results = []
    for i, user_input in enumerate(inputs, 1):
        print(f"[{i}/{len(inputs)}] Processing: {user_input[:50]}{'...' if len(user_input) > 50 else ''}")
        try:
            response = await run_traced_agent(user_input)
            results.append({"input": user_input, "output": response, "error": None})
            print(f"  Done")
        except Exception as e:
            results.append({"input": user_input, "output": None, "error": str(e)})
            print(f"  Error: {e}")
        print()

    # Save results
    output_file = input_file.replace(".json", "_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print("=" * 60)
    print(f"Completed {len(inputs)} inputs")
    print(f"Results saved to {output_file}")


def main():
    """
    Entry point - runs the async main function.
    """
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
