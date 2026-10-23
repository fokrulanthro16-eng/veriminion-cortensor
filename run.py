"""
VeriMinion - 1-Command Unified Launcher
---------------------------------------
Starts the FastAPI backend serving both REST/SSE APIs and the compiled Tactical UI.
"""

import os
import sys
import uvicorn

# Ensure repository root is on PYTHONPATH
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from backend.core.storage import init_db

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    print(f"\n========================================================")
    print(f"  VERIMINION: DECENTRALIZED INFERENCE VALIDATOR")
    print(f"  OPENMINION 0.1 SDK X-RAY STUDIO (CORTENSOR HACKATHON #5)")
    print(f"========================================================")
    print(f"  -> Tactical Command Center: http://localhost:{port}")
    print(f"  -> Interactive OpenAPI Docs: http://localhost:{port}/docs")
    print(f"========================================================\n")
    uvicorn.run("backend.api.server:app", host=host, port=port, reload=False)
