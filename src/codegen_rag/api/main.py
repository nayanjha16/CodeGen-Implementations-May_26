"""FastAPI backend — five endpoints per the proposal's qualitative outcomes:
``/generate``, ``/document``, ``/translate``, ``/sql``, ``/rag``.

Run locally with::

    uvicorn codegen_rag.api.main:app --host 0.0.0.0 --port 8000

or via ``docker/Dockerfile.api``. Interactive API docs are auto-served at
``/docs`` (Swagger UI) and ``/redoc``.
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from codegen_rag import __version__
from codegen_rag.api.dependencies import (
    AppState,
    describe_available_checkpoints,
    get_app_state,
    get_codegen_model,
    get_llm_client,
    get_rag_indexes,
    get_schema_for_db,
    get_settings,
)
from codegen_rag.api.schemas import (
    DocumentRequest,
    DocumentResponse,
    ErrorResponse,
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    RAGRequest,
    RAGResponse,
    ScoreRequest,
    ScoreResponse,
    SQLRequest,
    SQLResponse,
    SQLScoreRequest,
    SQLScoreResponse,
    TranslateRequest,
    TranslateResponse,
)
from codegen_rag.models.generation_config import GenerationConfig
from codegen_rag.models.model_registry import LLMUnavailableError
from codegen_rag.rag.pipeline import RAGPipeline
from codegen_rag.sql.schema_injection import build_sql_prompt
from codegen_rag.tasks.code_translation import CodeTranslationTask
from codegen_rag.tasks.documentation_generation import DocumentationGenerationTask
from codegen_rag.tasks.program_synthesis import ProgramSynthesisTask
from codegen_rag.utils.logging_config import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="CodeGen Capstone API",
        description=(
            "Program synthesis, documentation generation, SQL generation, and "
            "RAG-augmented generation over codegen-350M-multi."
        ),
        version=__version__,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse, tags=["meta"])
    def health(state: AppState = Depends(get_app_state)) -> HealthResponse:
        settings = get_settings(state)
        # Merge the cheap disk-only check (accurate even before any request
        # has triggered a lazy model load) with whatever's already resolved,
        # so a checkpoint doesn't disappear from the report once loaded.
        checkpoints = describe_available_checkpoints(settings)
        checkpoints.update(state.active_checkpoints)
        return HealthResponse(
            status="ok",
            version=__version__,
            base_model=settings.base_model.name,
            active_checkpoints=checkpoints,
        )

    @app.post(
        "/generate",
        response_model=GenerateResponse,
        responses={500: {"model": ErrorResponse}},
        tags=["tasks"],
    )
    def generate(request: GenerateRequest, state: AppState = Depends(get_app_state)) -> GenerateResponse:
        model = get_codegen_model(state, language=request.language)
        settings = get_settings(state)
        gen_cfg = GenerationConfig(**settings.model["generation"]["program_synthesis"])
        task = ProgramSynthesisTask(model, gen_cfg, language=request.language)
        result = task.run({"intent": request.problem_description})
        return GenerateResponse(code=result["prediction"], language=request.language)

    @app.post(
        "/document",
        response_model=DocumentResponse,
        responses={500: {"model": ErrorResponse}},
        tags=["tasks"],
    )
    def document(request: DocumentRequest, state: AppState = Depends(get_app_state)) -> DocumentResponse:
        model = get_codegen_model(state, language=request.language)
        settings = get_settings(state)
        gen_cfg = GenerationConfig(**settings.model["generation"]["documentation_generation"])
        task = DocumentationGenerationTask(model, gen_cfg)
        result = task.run({"code": request.code})
        return DocumentResponse(docstring=result["prediction"])

    @app.post(
        "/translate",
        response_model=TranslateResponse,
        responses={500: {"model": ErrorResponse}},
        tags=["tasks"],
    )
    def translate(request: TranslateRequest, state: AppState = Depends(get_app_state)) -> TranslateResponse:
        # Select the model by the *target* language -- that's what's actually
        # being generated, so a Python->Rust translation should get the Rust
        # fine-tune's benefit even though the source is Python.
        model = get_codegen_model(state, language=request.target_language)
        settings = get_settings(state)
        gen_cfg = GenerationConfig(**settings.model["generation"]["code_translation"])
        task = CodeTranslationTask(
            model,
            gen_cfg,
            source_language=request.source_language,
            target_language=request.target_language,
        )
        result = task.run({"source_code": request.source_code})
        return TranslateResponse(
            translated_code=result["prediction"],
            source_language=request.source_language,
            target_language=request.target_language,
        )

    @app.post(
        "/sql",
        response_model=SQLResponse,
        responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
        tags=["tasks"],
    )
    def sql(request: SQLRequest, state: AppState = Depends(get_app_state)) -> SQLResponse:
        schema = get_schema_for_db(request.db_id, state)
        model = get_codegen_model(state)
        settings = get_settings(state)
        gen_cfg = GenerationConfig(**settings.model["generation"]["sql_generation"])

        prompt = build_sql_prompt(request.question, schema)
        completions = model.generate(prompt, gen_cfg)
        from codegen_rag.sql.sql_generation_task import SQLGenerationTask

        cleaned_sql = SQLGenerationTask(model).postprocess(completions[0]) if completions else ""
        return SQLResponse(sql=cleaned_sql, db_id=request.db_id)

    @app.post(
        "/rag",
        response_model=RAGResponse,
        responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
        tags=["tasks"],
    )
    def rag(request: RAGRequest, state: AppState = Depends(get_app_state)) -> RAGResponse:
        dense_index, ast_index = get_rag_indexes(state)
        model = get_codegen_model(state)

        def embed_fn(text: str):
            return model.embed([text]).numpy()[0]

        pipeline = RAGPipeline(
            dense_index=dense_index,
            ast_index=ast_index,
            embed_fn=embed_fn,
            strategy=request.strategy,
            top_k=request.top_k,
        )

        if request.use_llm:
            llm_client = get_llm_client(state)
            try:
                generate_fn = lambda prompt: llm_client.generate(prompt).text  # noqa: E731
                result = pipeline.generate(request.query, generate_fn)
            except LLMUnavailableError as exc:
                raise HTTPException(status_code=503, detail=str(exc)) from exc
        else:
            settings = get_settings(state)
            gen_cfg = GenerationConfig(**settings.model["generation"]["program_synthesis"])
            generate_fn = lambda prompt: model.generate(prompt, gen_cfg)[0]  # noqa: E731
            result = pipeline.generate(request.query, generate_fn)

        return RAGResponse(
            generation=result.generation,
            retrieved_count=len(result.retrieved_chunks),
            strategy=result.strategy,
            top_k=result.top_k,
            used_llm=request.use_llm,
        )

    @app.post(
        "/score",
        response_model=ScoreResponse,
        responses={500: {"model": ErrorResponse}},
        tags=["scoring"],
    )
    def score(request: ScoreRequest) -> ScoreResponse:
        """Score a single (prediction, reference) pair on demand -- the
        instant, per-query counterpart to the batch metrics the checkpoint
        notebooks compute over a whole dataset via Evaluator.evaluate_task().
        Lets the demo show CodeBLEU/BERTScore/exact-match for whatever the
        user just typed in, not only the pre-computed dataset-level baseline.
        """
        from codegen_rag.evaluation.metrics import compute_bertscore, compute_codebleu, exact_match

        em = exact_match([request.prediction], [request.reference])
        codebleu_result = compute_codebleu([request.prediction], [request.reference], language=request.language)
        bertscore_result = compute_bertscore([request.prediction], [request.reference])

        return ScoreResponse(
            exact_match=em,
            codebleu=codebleu_result.get("codebleu"),
            bertscore_f1=bertscore_result.get("f1"),
        )

    @app.post(
        "/score_sql",
        response_model=SQLScoreResponse,
        responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
        tags=["scoring"],
    )
    def score_sql(request: SQLScoreRequest, state: AppState = Depends(get_app_state)) -> SQLScoreResponse:
        """Execute the just-generated SQL (and, if supplied, a gold query)
        against the same database used to generate it -- instant per-query
        feedback, distinct from the batch execution_accuracy the checkpoint
        notebooks compute over the full Spider/BIRD eval split."""
        from codegen_rag.evaluation.metrics import _execute_sql, _results_match

        schema = get_schema_for_db(request.db_id, state)

        predicted_error: str | None = None
        predicted_result = None
        try:
            predicted_result = _execute_sql(request.predicted_sql, schema.db_path)
        except Exception as exc:  # sqlite3.Error and friends
            predicted_error = str(exc)

        execution_match: bool | None = None
        gold_error: str | None = None
        if request.gold_sql:
            try:
                gold_result = _execute_sql(request.gold_sql, schema.db_path)
                execution_match = predicted_result is not None and _results_match(predicted_result, gold_result)
            except Exception as exc:
                gold_error = str(exc)
                execution_match = False

        return SQLScoreResponse(
            executed_successfully=predicted_error is None,
            predicted_error=predicted_error,
            execution_match=execution_match,
            gold_error=gold_error,
        )

    return app


app = create_app()
