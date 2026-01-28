# Trip Planner Agent

An AI travel planning assistant that helps you research destinations, find restaurants, discover activities, and plan your perfect trip.

Built with Claude Agent SDK, Tavily Search, and LangSmith tracing.

## Features

- **Search destinations** - Research travel destinations, attractions, and culture
- **Find restaurants** - Discover great dining options by cuisine or location
- **Discover activities** - Find things to do and top attractions
- **Search accommodations** - Find hotels and lodging options
- **Get travel tips** - Practical advice on weather, safety, customs, and more

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get your API keys:**
   - **Anthropic API key** (required): https://console.anthropic.com
   - **Tavily API key** (required): https://tavily.com - Free tier: 1000 searches/month
   - **LangSmith API key** (optional): https://smith.langchain.com - For tracing

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your keys:
   ```
   ANTHROPIC_API_KEY=your_key_here
   TAVILY_API_KEY=your_key_here
   LANGSMITH_API_KEY=your_key_here  # optional
   LANGSMITH_TRACING=true           # optional
   ```

4. **Run the agent:**
   ```bash
   python main.py                          # Uses inputs.json by default
   python main.py custom.json              # Or specify a custom input file
   python main.py --parallel 5             # Run 5 queries in parallel
   python main.py --start 10 --end 20      # Process only inputs 10-19
   ```

## Usage

The agent runs in batch mode, processing queries from a JSON file.

**CLI options:**
```
python main.py [input_file] [options]

Options:
  --start N      Start index, 0-based (default: 0)
  --end N        End index, exclusive (default: all)
  --parallel N   Number of parallel requests (default: 1)
```

**Input format** (`inputs.json`):
```json
[
  "Plan a weekend trip to Portland, Oregon",
  "Find me the best Italian restaurants in Rome",
  "What are the top things to do in Tokyo?"
]
```

**Example queries:**
- "I want to plan a weekend trip to Portland, Oregon"
- "Find me the best Italian restaurants in Rome"
- "What are the top things to do in Tokyo?"
- "I need a budget hotel in Barcelona"
- "What's the best time to visit Iceland?"
- "Give me safety tips for traveling to Colombia"

Results are saved to `<input_file>_results_<start>_<end>.json`.

## LangSmith Tracing

If you configure LangSmith (optional), you'll see detailed traces of:
- Agent reasoning and decision-making
- Search queries being executed
- Tool invocations and results
- How the agent synthesizes information

Check your LangSmith dashboard at https://smith.langchain.com

## How It Works

The agent uses:
- **Claude Sonnet 4.5** for intelligent trip planning
- **Tavily Search** for real-time web search results
- **LangSmith** for observability and tracing
- **Claude Agent SDK** for agentic workflows

All tool calls and searches happen in the background - you just see the final, synthesized response!
