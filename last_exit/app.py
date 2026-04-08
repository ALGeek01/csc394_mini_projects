"""Legacy entrypoint: run the game with Uvicorn (see README)."""

from __future__ import annotations

if __name__ == "__main__":
    import uvicorn

    from main import app

    uvicorn.run(app, host="127.0.0.1", port=5000, reload=True)
