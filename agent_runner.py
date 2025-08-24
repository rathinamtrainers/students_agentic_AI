import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
import os

if __name__ == "__main__":
    agents_dir = os.path.dirname(os.path.abspath(__file__))
    app = get_fast_api_app(
        agents_dir=agents_dir,
        web=True,
        host="0.0.0.0",
        port=8010,
        reload_agents=True
    )

    print(f"Server is listening on http://0.0.0.0:8010")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8010,
        log_level="info",
    )
