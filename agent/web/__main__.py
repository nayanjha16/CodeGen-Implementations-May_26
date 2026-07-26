"""Run the agent web UI: python -m agent.web"""

from __future__ import annotations

import os

import uvicorn


def main() -> None:
    host = os.environ.get("AGENT_WEB_HOST", "127.0.0.1")
    port = int(os.environ.get("AGENT_WEB_PORT", "8080"))
    reload = os.environ.get("AGENT_WEB_RELOAD", "").lower() in {"1", "true", "yes"}
    uvicorn.run(
        "agent.web.app:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    main()
