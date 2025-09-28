"""
MCP Server with Token Introspection
"""
import click
from mcp.server import FastMCP
from pydantic import AnyHttpUrl
import logging
import datetime
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict
from mcp.server.auth.settings import AuthSettings

from token_verifier import IntrospectionTokenVerifier

logger = logging.getLogger(__name__)

class ResourceServerSettings(BaseSettings):
    """Settings for the MCP Server"""
    model_config = SettingsConfigDict(env_prefix="MCP_RESOURCE_")

    # Server Settings
    host: str = "localhost"
    port: int = 8001
    server_url: AnyHttpUrl = AnyHttpUrl(f"http://{host}:{port}")

    # Authorization Server Settings
    auth_server_url: AnyHttpUrl = AnyHttpUrl("http://localhost:9000")
    auth_server_introspection_endpoint: str = "http://localhost:9000/introspect"

    mcp_scope: str = "user"

    oauth_strict: bool = False


def create_resource_server(settings: ResourceServerSettings) -> FastMCP:

    token_verifier = IntrospectionTokenVerifier(
        introspection_endpoint=settings.auth_server_introspection_endpoint,
        server_url=str(settings.server_url),
        validate_resource=settings.oauth_strict
    )

    app = FastMCP(
        name="MCP Resource Server",
        host=settings.host,
        port=settings.port,
        debug=True,
        token_verifier=token_verifier,
        auth = AuthSettings(
            issuer_url = settings.auth_server_url,
            required_scopes = [settings.mcp_scope],
            resource_server_url = settings.server_url,
        )
    )

    @app.tool()
    async def get_time() -> dict[str, Any]:
        """
        Get the current server time.
        """
        now = datetime.datetime.now()

        return {
            "current_time": now.isoformat(),
            "timezone": "UTC",
            "timestamp": now.timestamp(),
            "formatted": now.strftime("%Y-%m-%d %H:%M:%S"),
            "message": "This is a simple MCP tool without authentication"
        }

    return app


@click.command()
@click.option("--port", default=8001, help="Port to bind the server to.")
@click.option("--auth-server", default="http://localhost:9000", help="Authorization server url")
def main(port: int, auth_server: str):
    """
    Run the MCP Server.
    """
    try:
        # Parse auth server URL
        auth_server_url = AnyHttpUrl(auth_server)

        # Create Settings
        host = "localhost"
        server_url = AnyHttpUrl(f"http://{host}:{port}")

        settings = ResourceServerSettings(
            host=host,
            port=port,
            server_url=server_url,
            auth_server_url = auth_server_url,
            auth_server_introspection_endpoint = f"{auth_server_url}/introspect",
            oauth_strict=False
        )
    except ValueError as e:
        logger.error(f"Configuration Error: {e}")
        logger.error("Provide valid authorization server url")
        return 1

    try:
        mcp_server = create_resource_server(settings)
        mcp_server.run(transport="streamable-http")
        logger.info("Server stopped")
        return 0
    except Exception as e:
        logger.exception("Server error")
        return 1

if __name__ == "__main__":
    main()