import logging
from fastmcp import FastMCP
import os
import asyncio

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# MCP Server
mcp = FastMCP("MCP Server on Cloud Run")

@mcp.tool()
def add(a: int, b: int) -> int:
    """
    USe this to add two numbers together.

    :param a: The first number
    :param b: The second number
    :return: The sum of the two numbers
    """

    logger.info(f" Added {a} and {b} and got the result {a + b}")
    return a + b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """
    USe this to subtract two numbers.

    :param a: The first number
    :param b: The second number
    :return: The difference of the two numbers
    """

    logger.info(f" Subtract:  {a} - {b}")
    return a - b

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"MCP server started on port {port}")
    asyncio.run(
        mcp.run_async(
            transport="streamable-http",
            host="0.0.0.0",
            port=port
        ))

