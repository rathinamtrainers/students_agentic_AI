import logging
from mcp.server.fastmcp.server import FastMCP
import click
from typing import Any
import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Create MCP Server
server = FastMCP("simple-mcp-server")

@server.tool()
def get_time() -> dict[str, Any]:
    """Get the current server time

    This is a simple tool that returns current time information.
    No authentication required - anyone can call this.
    """
    now = datetime.datetime.now()

    return {
        "current_time": now.isoformat(),
        "timezone": "local",
        "timestamp": now.timestamp(),
        "formatted": now.strftime("%Y-%m-%d %H:%M:%S"),
        "message": "This is a simple MCP tool without authentication"
    }

@server.tool()
def add_numbers(a: int, b: int) -> dict[str, Any]:
    """Add two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Dictionary with the sum and operation details.
    """
    result = a + b
    return {
        "operation": "addition",
        "input_a": a,
        "input_b": b,
        "result": result,
        "formula": f"{a} + {b} = {result}"
    }

@server.tool()
def greet_user(name: str) -> dict[str, Any]:
    """Greet a user by name.

    Args:
        name: Name of the person to greet.

    Returns:
        A personalized greeting message
    """
    return {
        "greeting": f"Hello {name}!",
        "message": f"Welcome to the simple MCP server, {name}!",
        "timestamp": datetime.datetime.now().isoformat()
    }

@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to.")
@click.option("--port", default=8000, help="Port to bind the server to.")
def main(port: int, host: str):
    """Run the simple MCP server"""
    logger.info(f"Starting simple MCP server on {host}:{port}")
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
