#!/usr/bin/env python3
import os
import sys
import json
import asyncio
import argparse
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


async def process_single(index: int, user_input: str, total: int, semaphore: asyncio.Semaphore) -> dict:
    """Process a single input with semaphore for concurrency control."""
    async with semaphore:
        print(f"[{index}/{total}] Starting: {user_input[:50]}{'...' if len(user_input) > 50 else ''}")
        try:
            response = await run_traced_agent(user_input)
            print(f"[{index}/{total}] Done")
            return {"input": user_input, "output": response, "error": None}
        except Exception as e:
            print(f"[{index}/{total}] Error: {e}")
            return {"input": user_input, "output": None, "error": str(e)}


async def main_async():
    """
    Batch run the agent on inputs from a JSON file.
    """
    parser = argparse.ArgumentParser(description="Trip Planner Agent - Batch Mode")
    parser.add_argument("input_file", nargs="?", default="inputs.json", help="JSON file with inputs")
    parser.add_argument("--start", type=int, default=0, help="Start index (0-based)")
    parser.add_argument("--end", type=int, default=None, help="End index (exclusive)")
    parser.add_argument("--parallel", "-p", type=int, default=1, help="Number of parallel requests")
    args = parser.parse_args()

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

    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        print("Usage: python main.py [inputs.json] [--start N] [--end N] [--parallel N]")
        print()
        print("Expected JSON format:")
        print('  ["query 1", "query 2", ...]')
        sys.exit(1)

    # Load inputs from JSON file
    with open(args.input_file, "r") as f:
        all_inputs = json.load(f)

    if not isinstance(all_inputs, list):
        print("Error: JSON file should contain a list of input strings")
        sys.exit(1)

    # Slice inputs based on start/end
    end = args.end if args.end is not None else len(all_inputs)
    inputs = all_inputs[args.start:end]

    print("=" * 60)
    print("Trip Planner Agent - Batch Mode")
    print("=" * 60)
    print(f"Processing inputs {args.start} to {end} ({len(inputs)} total) from {args.input_file}")
    print(f"Parallelism: {args.parallel}")
    print()

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(args.parallel)

    # Create tasks for all inputs
    tasks = [
        process_single(args.start + i + 1, user_input, len(all_inputs), semaphore)
        for i, user_input in enumerate(inputs)
    ]

    # Run all tasks concurrently (semaphore limits actual parallelism)
    results = await asyncio.gather(*tasks)

    # Save results
    output_file = args.input_file.replace(".json", f"_results_{args.start}_{end}.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print()
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
