"""
FastAPI entrypoint for the ChatKit-powered Agentic Researcher.

Run with:
    uv run uvicorn chatkit_app:app --reload
    # or: uvicorn chatkit_app:app --reload

Then open http://localhost:8000/
"""

from fastapi import FastAPI, Request
from fastapi.responses import Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from chatkit.server import StreamingResult
from chatkit_server import ResearchChatKitServer

app = FastAPI(title="Agentic Researcher — ChatKit")
server = ResearchChatKitServer()


@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    result = await server.process(await request.body(), context={})
    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")
    return Response(content=result.json, media_type="application/json")


# Serves static/index.html at "/" and any other files under static/ at their path.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
