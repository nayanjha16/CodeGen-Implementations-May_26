"""FastAPI web server for the AI Database Agent."""

from __future__ import annotations

import asyncio
from functools import partial
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from agent.config.settings import AgentSettings, get_settings
from agent.orchestration import AgentRunner, run_agent_graph
from agent.orchestration.state import AgentResult
from agent.web.examples import list_examples
from agent.web.schemas import HealthResponse, QueryRequest, QueryResponse

WEB_ROOT = Path(__file__).resolve().parent
TEMPLATES = Jinja2Templates(directory=str(WEB_ROOT / "templates"))

app = FastAPI(
    title="AI Database Agent",
    description="Chat UI for Text2SQL, SQL2NoSQL, and documentation tasks",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(WEB_ROOT / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    settings = get_settings()
    return TEMPLATES.TemplateResponse(
        request,
        "index.html",
        {
            "default_db_id": settings.demo.db_id or "chinook",
            "database_profile": settings.database_profile,
        },
    )


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        database_profile=settings.database_profile,
        demo_db_id=settings.demo.db_id or "chinook",
        codegen_api_url=settings.codegen_api_url,
        orchestrator_model=settings.ollama_model,
    )


@app.get("/api/examples")
async def examples() -> list[dict]:
    return [item.model_dump() for item in list_examples()]


def _run_agent_sync(
    settings: AgentSettings,
    user_message: str,
    *,
    explicit_intent: str | None,
    db_id: str | None,
    dataset: str | None,
    sql: str | None,
) -> AgentResult:
    with AgentRunner(settings=settings) as runner:
        return run_agent_graph(
            user_message,
            explicit_intent=explicit_intent,
            db_id=db_id,
            dataset=dataset,
            sql=sql,
            runner=runner,
        )


@app.post("/api/query", response_model=QueryResponse)
async def query(body: QueryRequest) -> QueryResponse:
    settings = get_settings()
    explicit_intent = None if body.intent == "auto" else body.intent

    user_message = body.message.strip()
    if explicit_intent == "sql2nosql" and body.sql and not body.message.strip():
        user_message = f"Convert this SQL to MongoDB:\n{body.sql.strip()}"
    elif not user_message and body.sql:
        user_message = body.sql.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message or SQL is required")

    try:
        result = await asyncio.to_thread(
            partial(
                _run_agent_sync,
                settings,
                user_message,
                explicit_intent=explicit_intent,
                db_id=body.db_id,
                dataset=body.dataset,
                sql=body.sql,
            )
        )
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    payload = result.to_dict()
    if not isinstance(payload.get("rows"), list):
        payload["rows"] = []
    return QueryResponse(**payload)


def create_app() -> FastAPI:
    return app
