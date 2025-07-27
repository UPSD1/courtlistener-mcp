# Essential imports for MCP client
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import json
from contextlib import AsyncExitStack
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Server parameters for your CourtListener MCP server
server_params = StdioServerParameters(
    command="python",
    args=["./courtlistener_server.py"],
    env={
            "COURTLISTENER_API_TOKEN": os.getenv("COURTLISTENER_API_TOKEN"),
            "MCP_TRANSPORT": "stdio"
        }
)
exit_stack = AsyncExitStack()

async def connect_to_mcp_server():
    stdio_transport = await exit_stack.enter_async_context(
        stdio_client(server_params)
    )
    read, write = stdio_transport
    
    session = await exit_stack.enter_async_context(
        ClientSession(read, write)
    )
    
    await session.initialize()
    
    # Log available tools
    tools_response = await session.list_tools()
    tool_names = [tool.name for tool in tools_response.tools]
    print(f"{len(tool_names)} Available tools")

    # Call a tool
    result = await session.call_tool(
        "advanced_legal_search", 
        arguments={"query": "constitutional privacy", "courts": ["scotus", "ca9"], "date_range": "last_year"}
    )

    print(result.content[0].text)
    
    # Close
    await exit_stack.aclose()

if __name__ == "__main__":
    asyncio.run(connect_to_mcp_server())
