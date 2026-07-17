"""FastAPI server for NL2Py, Java2Py, Code2Doc, comments, NL→Java→Python, and agentic solve."""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "inference"))
sys.path.insert(0, str(PROJECT_ROOT / "data" / "scripts"))

from generator import load_generator
from rag_pipeline import RAGPipeline
from prompt_templates import (
    format_code2doc_inference,
    format_comment_inference,
    format_java2py_inference,
    format_nl2java_inference,
    format_nl2py_inference,
)

_generator = None
_generators: dict = {}
_rag_pipelines: dict = {}
_model_path: str | None = None
_agent_ready = False
TASKS = ("nl2py", "java2py", "code2doc", "comments", "nl2java2py")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _generator, _model_path, _agent_ready
    try:
        _generator = load_generator("java2py")
        _model_path = os.environ.get("MODEL_ID") or getattr(_generator, "model_path", None)
        for task in TASKS:
            _generators[task] = _generator
        for task in ("nl2py", "java2py"):
            try:
                _rag_pipelines[task] = RAGPipeline(task=task)
            except Exception as e:
                print(f"Warning: could not load RAG for {task}: {e}")
        try:
            from agent.llms import set_codegen_generator

            set_codegen_generator(_generator)
            _agent_ready = True
        except Exception as e:
            print(f"Warning: agent wiring failed: {e}")
            _agent_ready = False
    except Exception as e:
        print(f"Warning: could not load model: {e}")
    yield
    _generators.clear()
    _rag_pipelines.clear()
    _generator = None
    _model_path = None
    _agent_ready = False


app = FastAPI(
    title="Code Generation Capstone API",
    description=(
        "NL-to-Python, Java-to-Python, Code2Doc, code comments, "
        "NL→Java→Python pipeline, and LangGraph agentic solve"
    ),
    version="1.3.0",
    lifespan=lifespan,
)


class NL2PyRequest(BaseModel):
    query: str = Field(..., description="Natural language description")
    use_rag: bool = Field(True, description="Use RAG few-shot retrieval")


class Java2PyRequest(BaseModel):
    java_code: str = Field(..., description="Java source code to translate")
    use_rag: bool = Field(True, description="Use RAG few-shot retrieval")


class Code2DocRequest(BaseModel):
    python_code: str = Field(..., description="Python source code to document")


class CommentRequest(BaseModel):
    python_code: str = Field(..., description="Python code without comments")


class NL2Java2PyRequest(BaseModel):
    prompt: str = Field(..., description="Natural language description of the desired program")


class AgentSolveRequest(BaseModel):
    prompt: str = Field("", description="Natural language request (Text-to-PL)")
    java_code: str = Field("", description="Optional Java input for PL-to-PL route")
    unit: Literal["function", "class"] = Field(
        "function",
        description="Generation granularity; use class for full-class / patterns",
    )
    use_rag: bool = Field(False, description="Enable RAG retrieve node")
    max_retries: int = Field(3, ge=0, le=10, description="Max Fix Agent attempts")
    pattern: str = Field("", description="Optional design-pattern name (e.g. Singleton)")
    repo_root: str = Field("", description="Optional toy repo path for repo-aware route")
    input_type: Literal["nl", "java", "pseudocode"] | None = Field(
        None, description="Force router input type"
    )
    problem_id: str = Field("", description="Optional problem-pack id to load defaults from")


class CodeResponse(BaseModel):
    code: str
    task: str
    prompt_used: str | None = None


class DocResponse(BaseModel):
    documentation: str
    task: str = "code2doc"
    prompt_used: str | None = None


class PipelineResponse(BaseModel):
    prompt: str
    java_code: str
    python_code: str
    task: str = "nl2java2py"


class AgentSolveResponse(BaseModel):
    prompt: str
    java_code: str
    python_code: str
    stdout: str
    stderr: str
    judge_yes: bool
    judge_reason: str
    attempts: int
    unit: str
    route: str
    trace: list[dict[str, Any]]
    task: str = "agent_solve"


class AgentGenerateRequest(BaseModel):
    prompt: str = Field(..., description="Natural language request for Generate Agent")
    unit: Literal["function", "class"] = Field("function")
    use_rag: bool = Field(False)


class AgentGenerateResponse(BaseModel):
    prompt: str
    java_code: str
    python_code: str
    unit: str
    route: str
    trace: list[dict[str, Any]]
    task: str = "agent_generate"


class AgentFixRequest(BaseModel):
    prompt: str = Field("", description="Original user request / intent")
    python_code: str = Field(..., description="Broken or incomplete Python to repair")
    runtime: str = Field("", description="Stdout/stderr or error message from execution")
    unit: Literal["function", "class"] = Field("function")


class AgentFixResponse(BaseModel):
    prompt: str
    python_code: str
    ast_info: str
    unit: str
    runtime: str
    trace: list[dict[str, Any]]
    task: str = "agent_fix"


def _require_generator(task: str):
    if task not in _generators or _generators[task] is None:
        raise HTTPException(status_code=503, detail=f"{task} model not loaded")
    return _generators[task]


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "models_loaded": list(_generators.keys()),
        "model_path": _model_path,
        "shared_generator": _generator is not None,
        "agent_ready": _agent_ready,
    }


@app.post("/nl2py", response_model=CodeResponse)
async def nl2py(request: NL2PyRequest):
    gen = _require_generator("nl2py")

    prompt = format_nl2py_inference(request.query)
    if request.use_rag and "nl2py" in _rag_pipelines:
        prompt = _rag_pipelines["nl2py"].build_prompt(request.query)

    code = gen.generate(prompt)
    return CodeResponse(code=code, task="nl2py", prompt_used=prompt if request.use_rag else None)


@app.post("/java2py", response_model=CodeResponse)
async def java2py(request: Java2PyRequest):
    gen = _require_generator("java2py")

    prompt = format_java2py_inference(request.java_code)
    if request.use_rag and "java2py" in _rag_pipelines:
        prompt = _rag_pipelines["java2py"].build_prompt(request.java_code)

    code = gen.generate(prompt)
    return CodeResponse(code=code, task="java2py", prompt_used=prompt if request.use_rag else None)


@app.post("/code2doc", response_model=DocResponse)
async def code2doc(request: Code2DocRequest):
    gen = _require_generator("code2doc")

    prompt = format_code2doc_inference(request.python_code)
    documentation = gen.generate(prompt, response_type="doc")
    return DocResponse(documentation=documentation, prompt_used=prompt)


@app.post("/comments", response_model=CodeResponse)
async def add_comments(request: CommentRequest):
    gen = _require_generator("comments")

    prompt = format_comment_inference(request.python_code)
    code = gen.generate(prompt)
    return CodeResponse(code=code, task="comments", prompt_used=prompt)


@app.post("/nl2java2py", response_model=PipelineResponse)
async def nl2java2py(request: NL2Java2PyRequest):
    """Automated pipeline: natural language → Java → Python."""
    gen = _require_generator("nl2java2py")

    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="prompt must not be empty")

    java_prompt = format_nl2java_inference(request.prompt)
    java_code = gen.generate(java_prompt, response_type="code")
    if not java_code.strip():
        raise HTTPException(status_code=502, detail="NL→Java step produced empty output")

    py_prompt = format_java2py_inference(java_code)
    python_code = gen.generate(py_prompt, response_type="code")

    return PipelineResponse(
        prompt=request.prompt,
        java_code=java_code,
        python_code=python_code,
        task="nl2java2py",
    )


@app.post("/agent/solve", response_model=AgentSolveResponse)
async def agent_solve(request: AgentSolveRequest):
    """LangGraph agent: Codegen (NL→Java→Python) + Fix + LLM judge loop."""
    if _generator is None:
        raise HTTPException(status_code=503, detail="codegen model not loaded")

    prompt = request.prompt
    java_code = request.java_code
    unit = request.unit
    use_rag = request.use_rag
    max_retries = request.max_retries
    pattern = request.pattern
    repo_root = request.repo_root
    input_type = request.input_type

    if request.problem_id.strip():
        try:
            from agent.problems import get_problem

            prob = get_problem(request.problem_id.strip())
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        prompt = prompt or prob.get("nl_prompt", "")
        java_code = java_code or prob.get("java_code", "")
        unit = prob.get("unit", unit)
        use_rag = bool(prob.get("use_rag", use_rag))
        pattern = pattern or prob.get("pattern", "")
        repo_root = repo_root or prob.get("repo_root", "")
        input_type = input_type or prob.get("input_type")

    if not prompt.strip() and not java_code.strip():
        raise HTTPException(status_code=400, detail="prompt or java_code is required")

    from agent.graph import solve
    from agent.llms import set_codegen_generator

    set_codegen_generator(_generator)
    try:
        result = solve(
            prompt,
            java_code=java_code,
            unit=unit,
            use_rag=use_rag,
            max_retries=max_retries,
            pattern=pattern,
            repo_root=repo_root,
            input_type=input_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"agent failed: {e}") from e

    return AgentSolveResponse(
        prompt=result.get("nl_prompt") or prompt,
        java_code=result.get("java_code") or "",
        python_code=result.get("python_code") or "",
        stdout=result.get("stdout") or "",
        stderr=result.get("stderr") or "",
        judge_yes=bool(result.get("judge_yes")),
        judge_reason=result.get("judge_reason") or "",
        attempts=int(result.get("attempts") or 0),
        unit=result.get("unit") or unit,
        route=result.get("route") or "",
        trace=list(result.get("trace") or []),
    )


@app.get("/agent/problems")
async def agent_problems():
    """List Phase-2 problem pack entries."""
    from agent.problems import load_problem_pack

    return {"problems": load_problem_pack()}


@app.post("/agent/generate", response_model=AgentGenerateResponse)
async def agent_generate(request: AgentGenerateRequest):
    """Generate Agent only: NL → Java → Python (no execute/judge/fix)."""
    if _generator is None:
        raise HTTPException(status_code=503, detail="codegen model not loaded")
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="prompt must not be empty")

    from agent.llms import set_codegen_generator
    from agent.ui_runners import run_generate_agent

    set_codegen_generator(_generator)
    try:
        result = run_generate_agent(
            request.prompt,
            unit=request.unit,
            use_rag=request.use_rag,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"generate agent failed: {e}") from e

    return AgentGenerateResponse(
        prompt=result["prompt"],
        java_code=result["java_code"],
        python_code=result["python_code"],
        unit=result["unit"],
        route=result["route"],
        trace=result["trace"],
    )


@app.post("/agent/fix", response_model=AgentFixResponse)
async def agent_fix(request: AgentFixRequest):
    """Fix Agent only: repair Python given NL + code + runtime/error."""
    if _generator is None:
        raise HTTPException(status_code=503, detail="codegen model not loaded")
    if not request.python_code.strip():
        raise HTTPException(status_code=400, detail="python_code must not be empty")

    from agent.llms import set_codegen_generator
    from agent.ui_runners import run_fix_agent

    set_codegen_generator(_generator)
    try:
        result = run_fix_agent(
            request.prompt,
            request.python_code,
            runtime=request.runtime,
            unit=request.unit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"fix agent failed: {e}") from e

    return AgentFixResponse(
        prompt=result["prompt"],
        python_code=result["python_code"],
        ast_info=result["ast_info"],
        unit=result["unit"],
        runtime=result["runtime"],
        trace=result["trace"],
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
