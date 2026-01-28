import os
import sys
from typing import Any
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, tool, create_sdk_mcp_server
from tavily import TavilyClient


def get_tavily_client():
    """Get Tavily client with API key from environment."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in environment")
    return TavilyClient(api_key=api_key)


@tool(
    "search_destinations",
    "Search for information about travel destinations, including attractions, culture, best time to visit, and general overview.",
    {
        "destination": str,
        "specific_interest": str,
    },
)
async def search_destinations(args: dict[str, Any]) -> dict[str, Any]:
    """
    Search for destination information.
    """
    destination = args["destination"]
    specific_interest = args.get("specific_interest", "")

    try:
        client = get_tavily_client()

        # Build search query
        if specific_interest:
            query = f"{destination} travel guide {specific_interest}"
        else:
            query = f"{destination} travel guide attractions things to do"

        response = client.search(query, max_results=5)

        result_text = f"Destination Information for {destination}:\n\n"

        for i, result in enumerate(response.get('results', []), 1):
            result_text += f"{i}. {result['title']}\n"
            result_text += f"   {result['content']}\n"
            result_text += f"   Source: {result['url']}\n\n"

        if not response.get('results'):
            result_text += "No results found. Try a different destination or query."

        return {"content": [{"type": "text", "text": result_text}]}

    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error searching destinations: {str(e)}"}]}


@tool(
    "search_restaurants",
    "Search for restaurants and dining options in a specific location.",
    {
        "location": str,
        "cuisine_or_type": str,
    },
)
async def search_restaurants(args: dict[str, Any]) -> dict[str, Any]:
    """
    Search for restaurants in a location.
    """
    location = args["location"]
    cuisine_or_type = args.get("cuisine_or_type", "")

    try:
        client = get_tavily_client()

        # Build search query
        if cuisine_or_type:
            query = f"best {cuisine_or_type} restaurants in {location}"
        else:
            query = f"best restaurants in {location}"

        response = client.search(query, max_results=5)

        result_text = f"Restaurant Recommendations for {location}:\n\n"

        for i, result in enumerate(response.get('results', []), 1):
            result_text += f"{i}. {result['title']}\n"
            result_text += f"   {result['content']}\n"
            result_text += f"   Source: {result['url']}\n\n"

        if not response.get('results'):
            result_text += "No results found. Try a different location or cuisine type."

        return {"content": [{"type": "text", "text": result_text}]}

    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error searching restaurants: {str(e)}"}]}


@tool(
    "search_activities",
    "Search for activities, attractions, and things to do in a location.",
    {
        "location": str,
        "activity_type": str,
    },
)
async def search_activities(args: dict[str, Any]) -> dict[str, Any]:
    """
    Search for activities and attractions.
    """
    location = args["location"]
    activity_type = args.get("activity_type", "")

    try:
        client = get_tavily_client()

        # Build search query
        if activity_type:
            query = f"{activity_type} things to do in {location}"
        else:
            query = f"top attractions and things to do in {location}"

        response = client.search(query, max_results=5)

        result_text = f"Activities and Attractions in {location}:\n\n"

        for i, result in enumerate(response.get('results', []), 1):
            result_text += f"{i}. {result['title']}\n"
            result_text += f"   {result['content']}\n"
            result_text += f"   Source: {result['url']}\n\n"

        if not response.get('results'):
            result_text += "No results found. Try a different location or activity type."

        return {"content": [{"type": "text", "text": result_text}]}

    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error searching activities: {str(e)}"}]}


@tool(
    "search_accommodations",
    "Search for hotels, lodging, and accommodation options in a location.",
    {
        "location": str,
        "accommodation_type": str,
    },
)
async def search_accommodations(args: dict[str, Any]) -> dict[str, Any]:
    """
    Search for accommodation options.
    """
    location = args["location"]
    accommodation_type = args.get("accommodation_type", "hotels")

    try:
        client = get_tavily_client()

        # Build search query
        query = f"best {accommodation_type} in {location}"

        response = client.search(query, max_results=5)

        result_text = f"Accommodation Options in {location}:\n\n"

        for i, result in enumerate(response.get('results', []), 1):
            result_text += f"{i}. {result['title']}\n"
            result_text += f"   {result['content']}\n"
            result_text += f"   Source: {result['url']}\n\n"

        if not response.get('results'):
            result_text += "No results found. Try a different location or accommodation type."

        return {"content": [{"type": "text", "text": result_text}]}

    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error searching accommodations: {str(e)}"}]}


@tool(
    "get_travel_tips",
    "Get travel tips, advice, and practical information for a destination (weather, safety, local customs, budget, etc).",
    {
        "destination": str,
        "tip_category": str,
    },
)
async def get_travel_tips(args: dict[str, Any]) -> dict[str, Any]:
    """
    Get travel tips and practical information.
    """
    destination = args["destination"]
    tip_category = args.get("tip_category", "general travel tips")

    try:
        client = get_tavily_client()

        # Build search query
        query = f"{destination} {tip_category} travel advice"

        response = client.search(query, max_results=5)

        result_text = f"Travel Tips for {destination} ({tip_category}):\n\n"

        for i, result in enumerate(response.get('results', []), 1):
            result_text += f"{i}. {result['title']}\n"
            result_text += f"   {result['content']}\n"
            result_text += f"   Source: {result['url']}\n\n"

        if not response.get('results'):
            result_text += "No results found. Try a different destination or category."

        return {"content": [{"type": "text", "text": result_text}]}

    except Exception as e:
        return {"content": [{"type": "text", "text": f"Error getting travel tips: {str(e)}"}]}


async def run_agent(user_message: str, api_key: str) -> str:
    """
    Run the trip planner agent with a user message.

    Args:
        user_message: The user's request
        api_key: Anthropic API key

    Returns:
        The agent's final response
    """
    # Create SDK MCP server with all trip planning tools
    trip_tools_server = create_sdk_mcp_server(
        name="trip_tools",
        version="1.0.0",
        tools=[
            search_destinations,
            search_restaurants,
            search_activities,
            search_accommodations,
            get_travel_tips
        ],
    )

    # Set API key in environment for Claude SDK
    os.environ["ANTHROPIC_API_KEY"] = api_key

    options = ClaudeAgentOptions(
        model="claude-sonnet-4-5-20250929",
        system_prompt="""You are a thorough and enthusiastic travel planning assistant. You take pride in doing DEEP research to provide comprehensive trip recommendations.

IMPORTANT: You must ALWAYS call multiple tools to gather extensive information before responding. Don't be lazy - use your tools liberally!

When a user asks about a destination or trip, you should:
1. Search for general destination information (culture, attractions, overview)
2. Find specific activities and things to do
3. Research restaurant and dining options
4. Look into accommodation options
5. Get practical travel tips (weather, safety, best time to visit, local customs)

Call AT LEAST 3-5 tools for any meaningful trip planning request. The more research you do, the better your recommendations will be.

When synthesizing your response:
- Provide diverse options for different budgets and travel styles
- Include specific names, places, and practical details from your searches
- Mention sources when relevant
- Give actionable recommendations with context
- Be enthusiastic and paint a picture of the destination

Your goal is to give users such thorough, well-researched advice that they feel confident and excited about their trip!""",
        mcp_servers={"trip_tools": trip_tools_server},
        allowed_tools=[
            "mcp__trip_tools__search_destinations",
            "mcp__trip_tools__search_restaurants",
            "mcp__trip_tools__search_activities",
            "mcp__trip_tools__search_accommodations",
            "mcp__trip_tools__get_travel_tips"
        ],
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(user_message)

        # Collect all messages
        response_parts = []
        async for message in client.receive_response():
            # Try to extract text from various message formats
            if isinstance(message, str):
                response_parts.append(message)
            elif hasattr(message, 'text'):
                response_parts.append(message.text)
            elif hasattr(message, 'content'):
                if isinstance(message.content, str):
                    response_parts.append(message.content)
                elif isinstance(message.content, list):
                    for block in message.content:
                        if hasattr(block, 'text'):
                            response_parts.append(block.text)
                        elif isinstance(block, dict) and 'text' in block:
                            response_parts.append(block['text'])
            else:
                # Fallback: convert to string
                response_parts.append(str(message))

        result = "".join(response_parts).strip()
        return result if result else "No response from agent."
