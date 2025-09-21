import logging
import click
import asyncio

from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleMCPClient:
    """Simple MCP Client without authentication"""

    def __init__(self):
        self.session = None

    async def connect(self, server_command: str):
        """Connect to MCP Server using stdio transport.

        Args:
            server_command: Command to start the Simple MCP server.
        """
        logger.info(f"Connecting to MCP Server using stdio transport: {server_command}")

        # Connect using stdio transport
        # Create server parameters for stdio connection.
        command_parts = server_command.split()
        server_params = StdioServerParameters(
            command=command_parts[0], # python
            args=command_parts[1:], # simple_server.py
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                self.session = session

                # Initialize the session
                logger.info("Initializing MCP session...")
                await session.initialize()
                logger.info("MCP session successfully initialized...")

                # Run interactive session
                await self.run_interactive_session()


    async def run_interactive_session(self):
        """Run an interactive session with the MCP server."""
        logger.info("\nInteractive MCP Client (No Authentication required")
        logger.info("Commands:")
        logger.info("  list - List available tools")
        logger.info("  call <tool_name> [args] - Call a tool")
        logger.info("  quit - Exit the session")

        while True:
            try:
                command = input("mcp> ").strip()

                if not command:
                    continue

                if command == "quit":
                    logger.info("Goodbye!")
                    break
                elif command == "list":
                    await self.list_tools()
                    pass
                elif command.startswith("call "):
                    await self.call_tool(command[5:])    # Remove call prefix
                    pass
                else:
                    logger.warning(f"Unknown command: {command}")
            except KeyboardInterrupt:
                logger.info("Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error: {e}")

    async def list_tools(self):
        """List all available tools from the server"""
        try:
            response = await self.session.list_tools()
            tools = response.tools

            if not tools:
                logger.info("No tools available.")
                return

            logger.info(f"Available tools: {len(tools)}")
            for i, tool in enumerate(tools, 1):
                logger.info(f"{i}. {tool.name}")
                if tool.description:
                    logger.info(f"Description: {tool.description}")
                logger.info("")

        except Exception as e:
            logger.error(f"Error listing tools: {e}")

    async def call_tool(self, command: str):
        """Call a tool with arguments

        Args:
            command: Tool name and arguments (e.g., "get_time" or "add_numbers 5 3")
        """

        try:
            parts = command.split()
            if not parts:
                logger.info("No tool specified")
                return

            tool_name = parts[0]
            args = parts[1:]

            # Parse arguments based on tool.
            tool_args = {}
            if tool_name == "add_numbers" and len(args) >= 2:
                tool_args = {
                    "a": int(args[0]),
                    "b": int(args[1])
                }
            elif tool_name == "greet_user" and len(args) >= 1:
                tool_args = {
                    "name": args[0]
                }

            logger.info(f"Calling tool: {tool_name} with arguments: {tool_args}")
            response = await self.session.call_tool(tool_name, arguments=tool_args)

            logger.info(f"Tool: {tool_name} result: ")

            if hasattr(response, 'content') and response.content:
                for content in response.content:
                    if hasattr(content, 'text'):
                        logger.info(content.text)
                    else:
                        logger.info(str(content))
            else:
                logger.info(str(response))

            logger.info("")


        except ValueError as e:
            logger.error(f"Invalid arguments: {e}")
        except Exception as e:
            logger.error(f"Error calling tool: {e}")




@click.command()
@click.option("--server_command", default="python simple_server.py",
              help="Command to start the Simple MCP server.")
def main(server_command: str):
    """Run the simple MCP Client"""

    client = SimpleMCPClient()
    asyncio.run(client.connect(server_command))

if __name__ == "__main__":
    main()
