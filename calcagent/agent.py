from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams

calc_mcp_server = MCPToolset(
        connection_params = StreamableHTTPConnectionParams(
            url = "https://mcp-server-762595014021.us-central1.run.app/mcp"
        )
    )

agent_instruction = """
You are a calculator support agent. 

You can access calculator tools that can help you with:
addition (add): Add two numbers together.
subtraction (subtract): Subtract two numbers.
"""

root_agent = Agent(
    model = "gemini-2.5-flash",
    name = "Calculator_support_agent",
    instruction=agent_instruction,
    tools = [calc_mcp_server]
)