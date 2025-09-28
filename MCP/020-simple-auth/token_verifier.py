import logging
import httpx
from mcp.server.auth.provider import TokenVerifier, AccessToken

logger = logging.getLogger(__name__)


class IntrospectionTokenVerifier(TokenVerifier):
    """
    Simple Introspection Token Verifier
    """

    def __init__(
            self,
            introspection_endpoint: str,
            server_url: str,
            validate_resource: bool = False
    ):
        self.introspection_endpoint = introspection_endpoint
        self.server_url = server_url
        self.validate_resource = validate_resource

    async def verify_token(self, token: str) -> AccessToken | None:
        """Verify token via introspection endpoint"""

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10, connect=5),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
            verify=True
        ) as client:
            try:
                response = await client.post(
                    self.introspection_endpoint,
                    data={
                        "token": token
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )

                if response.status_code != 200:
                    logger.error(f"Failed to verify token: {response.status_code}: {response.text}")
                    return None

                data = response.json()
                if not data.get("active"):
                    logger.error("Token is not active")
                    return None

                return AccessToken(
                    token=token,
                    expires_at=data.get("exp"),
                    client_id=data.get("client_id"),
                    scopes=data.get("Scope"),
                    resource=data.get("aud")
                )
            except Exception as e:
                logger.warning(f"Token Introspection failed: {e}")
                return None

    #TODO: Implement _is_valid_response() and _is_valid_resource()