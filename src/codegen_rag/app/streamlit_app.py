"""Streamlit UI — one tab per task, plus a results dashboard, calling the
FastAPI backend.

Run with::

    streamlit run src/codegen_rag/app/streamlit_app.py

Configure the backend location via the ``API_BASE_URL`` environment variable
(defaults to ``http://localhost:8000``, i.e. ``scripts/serve_api.py`` running
locally, or the ``api`` service name in ``docker-compose.yml``).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st

from codegen_rag.app.api_client import APIClient, APIClientError
from codegen_rag.config import load_settings

st.set_page_config(page_title="CodeGen Capstone", layout="wide", page_icon="🧬")

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
client = APIClient(base_url=API_BASE_URL)


# ---------------------------------------------------------------------------
# Results/metrics helpers
# ---------------------------------------------------------------------------


def _resolve_results_dir() -> Path:
    """Locate the ``results/`` directory that holds comparison_table.csv,
    the markdown reports, and the evaluation charts.

    Streamlit runs as its own OS process (launched via ``subprocess.Popen``),
    so it never sees the ``root_dir`` relocation that ``bootstrap_environment``
    applies in-memory to the notebook kernel's Settings singleton. The actual
    files are still shared on disk though (same Colab VM), so we check the
    Drive-persisted location directly before falling back to the plain
    repo-relative path used for local/non-Colab runs.
    """
    settings = load_settings()
    drive_candidate = Path("/content/drive/MyDrive") / settings.project.drive_subdir / "results"
    if drive_candidate.exists():
        return drive_candidate
    return settings.path_for("results")


@st.cache_data(ttl=30)
def _load_comparison_table() -> pd.DataFrame:
    path = _resolve_results_dir() / "comparison_table.csv"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def _metric_row_for(task: str, model_tier: str | None = None) -> pd.Series | None:
    df = _load_comparison_table()
    if df.empty:
        return None
    subset = df[df["task"] == task]
    if model_tier is not None:
        subset = subset[subset["model_tier"] == model_tier]
    if subset.empty:
        return None
    return subset.iloc[0]


def _fmt(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "—"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _show_baseline_metrics(task: str, model_tier: str | None = None) -> None:
    """Render a small 'before' metrics strip under a task's input form, so
    the score you're comparing your generated output against is visible
    right there rather than buried in a notebook or chat history."""
    row = _metric_row_for(task, model_tier)
    if row is None:
        st.caption(
            "No baseline evaluation found yet for this task — run the "
            "checkpoint notebooks to populate `comparison_table.csv`."
        )
        return
    with st.container(border=True):
        st.caption(f"Baseline performance ({row['model_tier']}, n={int(row['n_examples'])})")
        cols = st.columns(4)
        cols[0].metric("Exact match", _fmt(row.get("exact_match")))
        cols[1].metric("CodeBLEU", _fmt(row.get("codebleu")))
        cols[2].metric("BERTScore F1", _fmt(row.get("bertscore_f1")))
        cols[3].metric("Execution acc.", _fmt(row.get("execution_accuracy")))


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div style="padding: 1.25rem 1.5rem; border-radius: 0.75rem;
                background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
                margin-bottom: 1rem;">
      <div style="color: white; font-size: 1.6rem; font-weight: 700;">
        🧬 CodeGen: Small-LM + RAG for Software Engineering Tasks
      </div>
      <div style="color: #e0e7ff; font-size: 0.95rem; margin-top: 0.25rem;">
        AIML PGCP Capstone &middot; Group 39, Batch 26 &middot; Checkpoints 1&ndash;4
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(f"Backend: {API_BASE_URL}")

with st.sidebar:
    st.subheader("Backend status")
    if st.button("Check health"):
        try:
            health = client.health()
            st.success(f"OK — serving {health.get('base_model')}")
            active = {lang: path for lang, path in (health.get("active_checkpoints") or {}).items() if path}
            if active:
                for lang, path in active.items():
                    st.caption(f"🏆 {lang}: fine-tuned checkpoint active ({Path(path).name})")
            else:
                st.caption("No fine-tuned checkpoints active yet — serving the base model for every language.")
        except APIClientError as exc:
            st.error(str(exc))

    st.divider()
    st.caption("Evaluation data source")
    st.code(str(_resolve_results_dir()), language=None)

tab_generate, tab_document, tab_translate, tab_sql, tab_rag, tab_results = st.tabs(
    [
        "Program Synthesis",
        "Documentation",
        "Code Translation",
        "SQL Generation",
        "RAG",
        "📊 Evaluation Results",
    ]
)

with tab_generate:
    st.subheader("Program Synthesis")
    _show_baseline_metrics("program_synthesis", "small_lm_baseline")
    problem_description = st.text_area(
        "Problem description", placeholder="Write a function that reverses a string", height=120
    )
    language = st.selectbox("Language", ["python", "java", "cpp", "rust"], key="gen_lang")
    if st.button("Generate code", key="gen_btn", type="primary"):
        if not problem_description.strip():
            st.warning("Enter a problem description first.")
        else:
            try:
                with st.spinner("Generating..."):
                    result = client.generate(problem_description, language)
                st.code(result["code"], language=language)
            except APIClientError as exc:
                st.error(str(exc))

with tab_document:
    st.subheader("Documentation Generation")
    _show_baseline_metrics("documentation_generation", "small_lm_baseline")
    code_input = st.text_area(
        "Source code", placeholder="def add(a, b):\n    return a + b", height=160
    )
    doc_language = st.selectbox("Language", ["python", "java", "cpp"], key="doc_lang")
    if st.button("Generate documentation", key="doc_btn", type="primary"):
        if not code_input.strip():
            st.warning("Paste some code first.")
        else:
            try:
                with st.spinner("Generating..."):
                    result = client.document(code_input, doc_language)
                st.text_area("Generated docstring", result["docstring"], height=150)
            except APIClientError as exc:
                st.error(str(exc))

with tab_translate:
    st.subheader("Code Translation (PL-to-PL)")
    _show_baseline_metrics("code_translation", "small_lm_baseline")
    st.caption(
        "Note: CoDocBench (the source dataset for this task) has no `target_code` "
        "field, so exact-match/CodeBLEU/BERTScore are unscored (—) for this task — "
        "a known pre-existing data gap, not a bug. Generation below still runs live."
    )
    source_code = st.text_area(
        "Source code", placeholder="def add(a, b):\n    return a + b", height=160, key="translate_input"
    )
    tr_col1, tr_col2 = st.columns(2)
    with tr_col1:
        source_language = st.selectbox("Source language", ["python", "java", "cpp", "rust"], key="tr_src_lang")
    with tr_col2:
        target_language = st.selectbox(
            "Target language", ["java", "python", "cpp", "rust"], key="tr_tgt_lang"
        )
    if st.button("Translate code", key="translate_btn", type="primary"):
        if not source_code.strip():
            st.warning("Paste some source code first.")
        elif source_language == target_language:
            st.warning("Pick two different languages to translate between.")
        else:
            try:
                with st.spinner("Translating..."):
                    result = client.translate(source_code, source_language, target_language)
                st.code(result["translated_code"], language=target_language)
            except APIClientError as exc:
                st.error(str(exc))

with tab_sql:
    st.subheader("Natural Language to SQL")
    sql_col1, sql_col2 = st.columns(2)
    with sql_col1:
        _show_baseline_metrics("sql_generation_spider", "small_lm_baseline")
    with sql_col2:
        _show_baseline_metrics("sql_generation_birdbench", "small_lm_baseline")
    question = st.text_input("Question", placeholder="How many singers are there?")
    db_id = st.text_input("Database ID", placeholder="concert_singer")
    if st.button("Generate SQL", key="sql_btn", type="primary"):
        if not question.strip() or not db_id.strip():
            st.warning("Enter both a question and a database ID.")
        else:
            try:
                with st.spinner("Generating..."):
                    result = client.sql(question, db_id)
                st.code(result["sql"], language="sql")
            except APIClientError as exc:
                st.error(str(exc))

with tab_rag:
    st.subheader("Retrieval-Augmented Generation")
    rag_query = st.text_area("Query", placeholder="Write a function that sorts a list", height=100)
    col1, col2, col3 = st.columns(3)
    with col1:
        strategy = st.selectbox("Retrieval strategy", ["hybrid", "dense", "ast"])
    with col2:
        top_k = st.slider("Top-K", min_value=1, max_value=10, value=5)
    with col3:
        use_llm = st.checkbox("Use upper-bound LLM (Claude Sonnet 4)", value=False)

    if st.button("Run RAG", key="rag_btn", type="primary"):
        if not rag_query.strip():
            st.warning("Enter a query first.")
        else:
            try:
                with st.spinner("Retrieving + generating..."):
                    result = client.rag(rag_query, top_k=top_k, strategy=strategy, use_llm=use_llm)
                st.code(result["generation"])
                st.caption(
                    f"Retrieved {result['retrieved_count']} chunks via '{result['strategy']}' "
                    f"strategy (top_k={result['top_k']}, llm={result['used_llm']})"
                )
            except APIClientError as exc:
                st.error(str(exc))

with tab_results:
    st.subheader("Evaluation Results — all checkpoints")
    results_dir = _resolve_results_dir()
    df = _load_comparison_table()

    if df.empty:
        st.info(
            "No comparison_table.csv found yet. Run the Checkpoint 1-2 notebooks "
            "first to populate evaluation results."
        )
    else:
        st.caption(f"Loaded from {results_dir / 'comparison_table.csv'}")
        for task in sorted(df["task"].unique()):
            st.markdown(f"**{task}**")
            task_df = df[df["task"] == task].set_index("model_tier")
            display_cols = [
                c
                for c in ["n_examples", "exact_match", "codebleu", "bertscore_f1", "execution_accuracy"]
                if c in task_df.columns
            ]
            st.dataframe(task_df[display_cols], use_container_width=True)

    four_tier_chart = results_dir / "four_tier_comparison.png"
    topk_chart = results_dir / "topk_sweep.png"
    if four_tier_chart.exists() or topk_chart.exists():
        st.markdown("---")
        st.markdown("**Checkpoint 3 — RAG pipeline comparisons**")
        chart_cols = st.columns(2)
        if four_tier_chart.exists():
            chart_cols[0].image(str(four_tier_chart), caption="Small LM vs LLM vs LLM+RAG vs Fine-tuned+RAG")
        if topk_chart.exists():
            chart_cols[1].image(str(topk_chart), caption="Top-K retrieval sweep")

    for report_name, report_label in [
        ("checkpoint3_report.md", "Checkpoint 3 report (RAG pipeline)"),
        ("final_report.md", "Final report (Checkpoint 4)"),
    ]:
        report_path = results_dir / report_name
        if report_path.exists():
            with st.expander(report_label):
                st.markdown(report_path.read_text(encoding="utf-8"))
