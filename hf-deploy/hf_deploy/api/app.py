"""OpenAI-compatible FastAPI gateway for multi-adapter CodeGen."""

from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from hf_deploy import CLARIFY_INTENT, INTENTS
from hf_deploy.adapters.router import MultiAdapterRouter
from hf_deploy.api.schemas import (
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    HealthResponse,
    IntentMetadata,
    ModelCard,
    ModelList,
    UsageInfo,
)
from hf_deploy.classifier import IntentClassifier
from hf_deploy.config import load_manifest
from hf_deploy.prompt import CLARIFY_MESSAGE, format_generation_prompt

logger = logging.getLogger("hf_deploy.api")

_manifest: dict[str, Any] = {}
_router: MultiAdapterRouter | None = None
_classifier: IntentClassifier | None = None


def get_router() -> MultiAdapterRouter:
    if _router is None:
        raise RuntimeError("Router is not initialized")
    return _router


def get_classifier() -> IntentClassifier:
    if _classifier is None:
        raise RuntimeError("Classifier is not initialized")
    return _classifier


def _extract_user_text(messages: list[ChatMessage]) -> str:
    """Use the latest user message as the generation prompt."""
    for message in reversed(messages):
        if message.role == "user" and message.content.strip():
            return message.content
    raise HTTPException(status_code=400, detail="No user message found in messages.")


def _build_services(manifest: dict[str, Any]) -> tuple[MultiAdapterRouter, IntentClassifier]:
    classifier_cfg = manifest.get("classifier") or {}
    classifier = IntentClassifier(
        confidence_threshold=float(classifier_cfg.get("confidence_threshold", 0.45)),
        prefer_rules=bool(classifier_cfg.get("prefer_rules", True)),
        use_embeddings=True,
    )
    router = MultiAdapterRouter.from_manifest(manifest)
    return router, classifier


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _manifest, _router, _classifier
    # Tests may pre-inject mocks before TestClient starts.
    if _router is not None and _classifier is not None:
        yield
        return

    _manifest = load_manifest()
    _router, _classifier = _build_services(_manifest)
    if _manifest.get("eager_load", True):
        logger.info("Eager-loading base model and adapters...")
        _router.load()
    yield


app = FastAPI(
    title="CodeGen Multi-Adapter API",
    description=(
        "OpenAI-compatible chat completions API that classifies intent and "
        "routes to the matching LoRA adapter."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, Any]:
    """Simple landing page for Hugging Face Spaces."""
    return {
        "service": "codegen-multi-adapter",
        "docs": "/docs",
        "health": "/health",
        "openai_base": "/v1",
        "chat_completions": "/v1/chat/completions",
    }


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    router = get_router()
    return HealthResponse(status="ok", router=router.status())


@app.get("/v1/models", response_model=ModelList)
def list_models() -> ModelList:
    cards = [
        ModelCard(id="codegen-multi-adapter"),
        *[ModelCard(id=f"codegen-{intent}") for intent in INTENTS],
    ]
    return ModelList(data=cards)


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def chat_completions(body: ChatCompletionRequest) -> ChatCompletionResponse:
    if body.stream:
        raise HTTPException(status_code=400, detail="Streaming is not supported yet.")

    router = get_router()
    classifier = get_classifier()
    user_text = _extract_user_text(body.messages)

    if body.intent:
        intent = body.intent.strip().lower()
        if intent not in INTENTS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid intent '{body.intent}'. Expected one of: {list(INTENTS)}",
            )
        routing = IntentMetadata(
            intent=intent,
            confidence=1.0,
            method="override",
            scores={name: 1.0 if name == intent else 0.0 for name in INTENTS},
            adapter=intent,
            checkpoint_version=router.checkpoint_version,
        )
    else:
        result = classifier.classify(user_text)
        routing = IntentMetadata(
            intent=result.intent,
            confidence=result.confidence,
            method=result.method,
            scores=result.scores,
            adapter=result.intent if result.intent in INTENTS else None,
            checkpoint_version=router.checkpoint_version,
        )

    created = int(time.time())
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"

    if routing.intent == CLARIFY_INTENT:
        return ChatCompletionResponse(
            id=completion_id,
            created=created,
            model=body.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=CLARIFY_MESSAGE),
                    finish_reason="stop",
                )
            ],
            usage=UsageInfo(),
            codegen_routing=routing,
        )

    prompt = format_generation_prompt(routing.intent, user_text)
    try:
        output = router.generate(
            prompt,
            intent=routing.intent,
            max_new_tokens=body.max_tokens,
            temperature=body.temperature,
            top_p=body.top_p,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Generation failed")
        raise HTTPException(status_code=500, detail=f"Generation failed: {exc}") from exc

    return ChatCompletionResponse(
        id=completion_id,
        created=created,
        model=f"codegen-{routing.intent}",
        choices=[
            ChatCompletionChoice(
                index=0,
                message=ChatMessage(role="assistant", content=output),
                finish_reason="stop",
            )
        ],
        usage=UsageInfo(),
        codegen_routing=routing,
    )


def create_app() -> FastAPI:
    """Factory for tests / ASGI servers."""
    return app
