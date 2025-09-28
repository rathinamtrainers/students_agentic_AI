"""
Simple OAuth Provider for MCP Servers.
"""
import logging
import secrets
import time
from typing import Any

from mcp.shared.auth import OAuthClientInformationFull
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from mcp.server.auth.provider import (
    OAuthAuthorizationServerProvider,
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    RefreshToken,
    construct_redirect_uri
)

from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response

"""

from mcp.server.auth.provider import (

    
)
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
"""

# Create module-scope logger
logger = logging.getLogger(__name__)

class SimpleAuthSettings(BaseSettings):
    """Simple OAuth settings for student demo"""

    model_config = SettingsConfigDict(env_prefix="MCP_")

    # Demo user credentials
    demo_username: str = "demo_user"
    demo_password: str = "demo_password"

    # MCP OAuth scope
    mcp_scope: str = "user"

class SimpleOAuthProvider(OAuthAuthorizationServerProvider[AuthorizationCode, RefreshToken, AccessToken]):
    """
    Simple OAuth provider for MCP servers.

    1. Provides a simple login form for demo credentials.
    2. Issue MCP tokens after successful authentication.
    3. Maintain token state for interospection
    """

    def __init__(self, settings: SimpleAuthSettings, auth_callback_url: str, server_url: str):
        self.settings = settings
        self.auth_callback_url = auth_callback_url
        self.server_url = server_url

        # Dictionary of clients (key: Client Id, value: Client Information)
        self.clients: dict[str, OAuthClientInformationFull] = {}

        # State Mapping (key: state, value: dict[key: client_id/redirect_uri/..., value: string value])
        self.state_mapping: dict[str, dict[str, str | None]] = {}

        self.auth_codes: dict[str, AuthorizationCode] = {}
        self.user_data: dict[str, dict[str, Any]] = {}


    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        """Get client information by client ID"""
        return self.clients.get(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        """Register a new OAuth client"""
        self.clients[client_info.client_id] = client_info

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        """Generate an authorization URL for simple login flow"""

        client_state: str = params.state or secrets.token_hex(16)

        # Store state mapping for callbacks.
        self.state_mapping[client_state] = {
            "redirect_uri" : params.redirect_uri,
            "code_challenge": params.code_challenge,
            "redirect_uri_provided_explicitly": params.redirect_uri_provided_explicitly,
            "client_id": client.client_id,
            "resource": params.resource
        }

        auth_url = f"{self.auth_callback_url}?state={state}&client_id={client.client_id}"

        return auth_url

    async def get_login_page(self, state: str) -> HTMLResponse:
        """Gemnerate login page HTML for the given state"""

        if not state:
            raise HTTPException(status_code=400, detail="State is required")

        # Create simple login form HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MCP Demo Authentication</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px; }}
                .form-group {{ margin-bottom: 15px; }}
                input {{ width: 100%; padding: 8px; margin-top: 5px; }}
                button {{ background-color: #4CAF50; color: white; padding: 10px 15px; border: none; cursor: pointer; }}
            </style>
        </head>
        <body>
            <h2>MCP Demo Authentication</h2>
            <p>This is a simplified authentication demo. Use the demo credentials below:</p>
            <p><strong>Username:</strong> demo_user<br>
            <strong>Password:</strong> demo_password</p>

            <form action="{self.server_url.rstrip("/")}/login/callback" method="post">
                <input type="hidden" name="state" value="{state}">
                <div class="form-group">
                    <label>Username:</label>
                    <input type="text" name="username" value="demo_user" required>
                </div>
                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" name="password" value="demo_password" required>
                </div>
                <button type="submit">Sign In</button>
            </form>
        </body>
        </html>       
        """

        return HTMLResponse(content=html_content)

    async def handle_login_callback(self, request: Request) -> Response:
        """Handle login form submission callback"""
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        state = form.get("state")

        if not username or not password or not state:
            raise HTTPException(status_code=400, detail="Missing username, password, or state parameter")

        if not isinstance(username, str) or not isinstance(password, str) or not isinstance(state, str):
            raise HTTPException(status_code=400, detail="Invalid username, password, or state parameter")

        redirect_uri = await


    async def handle_simple_callback(self, username: str, password: str, state: str) -> str:
        """Handle simple authentication call back and return the redirect URI."""

        # Get state mapping
        state_data = self.state_mapping.get(state)
        if not state_data:
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        redirect_uri = state_data.get("redirect_uri")
        code_challenge = state_data.get("code_challenge")
        redirect_uri_provided_explicitly = state_data.get("redirect_uri_provided_explicitly")
        client_id = state_data.get("client_id")
        resource = state_data.get("resource")


        # Validate demo credentials
        if username != self.settings.demo_username or password != self.settings.demo_password:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        # Authentication Successful. Create MCP Authorization code.
        new_code = f"mcp_{secrets.token_hex(16)}"
        auth_code = AuthorizationCode(
            code=new_code,
            client_id=client_id,
            redirect_uri=AnyHttpUrl(redirect_uri),
            redirect_uri_provided_explicitly=redirect_uri_provided_explicitly == "True",
            expires_at=time.time() + 300,
            scopes=[self.settings.mcp_scope],
            code_challenge=code_challenge,
            resource=resource
        )
        self.auth_codes[new_code] = auth_code

        self.user_data[username] = {
            "username": username,
            "user_id": f"user_{secrets.token_hex(8)}",
            "authenticated_at": time.time()
        }

        del self.state_mapping[state]
        return construct_redirect_uri(redirect_uri, code=new_code, state=state)
    
