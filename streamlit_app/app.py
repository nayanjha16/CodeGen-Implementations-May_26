"""Streamlit UI for CodeGen project."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Add project root to path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluation.metrics import EvaluationMetrics
from src.query_engine.engine import QueryEngine
from src.sql2nosql.translator import SQLToNoSQLTranslator
from src.text2sql.prompt_builder import PromptBuilder
from src.text2sql.sql_generator import SQLGenerator
from src.utils.config import load_config

st.set_page_config(
    page_title="CodeGen Studio",
    page_icon="🗄️",
    layout="wide",
)

config = load_config()


@st.cache_resource
def get_sql_generator():
    return SQLGenerator(config=config)


@st.cache_resource
def get_translator():
    return SQLToNoSQLTranslator()


@st.cache_resource
def get_query_engine():
    return QueryEngine(config=config)


def page_text2sql():
    st.header("Text-to-SQL Generation")
    st.write("Generate SQL queries from natural language using CodeGen-350M-Multi.")

    col1, col2 = st.columns(2)
    with col1:
        schema = st.text_area(
            "Database Schema",
            value="Table students(id, name, age)\nTable courses(id, name, credits)",
            height=150,
        )
    with col2:
        question = st.text_area(
            "Natural Language Question",
            value="Show all students older than 20",
            height=150,
        )

    decoding = st.selectbox("Decoding Strategy", ["greedy", "beam"])

    if st.button("Generate SQL", type="primary"):
        with st.spinner("Generating SQL..."):
            result = get_sql_generator().generate(question, schema, decoding)
            st.subheader("Generated SQL")
            st.code(result["sql"], language="sql")
            with st.expander("Prompt & Raw Output"):
                st.text(result["prompt"])
                st.text(result["raw_output"])


def page_sql2nosql():
    st.header("SQL-to-NoSQL Translation")
    st.write("Translate SQL queries to MongoDB syntax.")

    sql = st.text_area(
        "SQL Query",
        value="SELECT name FROM users WHERE age > 20 ORDER BY name LIMIT 10",
        height=120,
    )

    if st.button("Translate to MongoDB", type="primary"):
        result = get_translator().translate(sql)
        st.subheader("MongoDB Query")
        st.code(result.get("mongodb_query", ""), language="javascript")
        if result.get("warnings"):
            st.warning("Warnings: " + "; ".join(result["warnings"]))


def page_interactive():
    st.header("Interactive Querying")
    st.write("Ask questions, generate SQL, execute, and view results.")

    schema = st.text_area(
        "Schema",
        value="Table students(id, name, age)",
        height=100,
    )
    question = st.text_input("Question", value="Show all students")
    db_path = st.text_input("Database Path (optional)", value="")

    if st.button("Run Query Pipeline", type="primary"):
        with st.spinner("Processing..."):
            engine = get_query_engine()
            result = engine.process(
                question,
                schema,
                db_path if db_path else None,
            )

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Generated SQL")
                st.code(result["sql"], language="sql")
            with col2:
                st.subheader("MongoDB Translation")
                st.code(result["nosql"].get("mongodb_query", ""), language="javascript")

            st.subheader("Validation")
            st.json(result["validation"])

            st.subheader("Execution Results")
            if result["execution"]["success"]:
                st.dataframe(pd.DataFrame(result["execution"]["rows"]))
            else:
                st.info(result["execution"].get("error", "No execution performed"))

            st.subheader("Explanation")
            st.text(result["explanation"])


def page_evaluation():
    st.header("Evaluation Dashboard")
    st.write("View benchmark metrics and compare results.")

    tab1, tab2 = st.columns(2)
    with tab1:
        st.subheader("Sample Evaluation")
        predictions = st.text_area(
            "Predictions (one per line)",
            value="SELECT name FROM students WHERE age > 20\nSELECT * FROM courses",
        )
        references = st.text_area(
            "References (one per line)",
            value="SELECT name FROM students WHERE age > 20\nSELECT id, name FROM courses",
        )

        if st.button("Compute Metrics"):
            preds = [p.strip() for p in predictions.strip().split("\n") if p.strip()]
            refs = [r.strip() for r in references.strip().split("\n") if r.strip()]
            if len(preds) == len(refs):
                metrics = EvaluationMetrics().evaluate_all(preds, refs)
                st.json(metrics)
            else:
                st.error("Predictions and references must have the same number of lines.")

    with tab2:
        st.subheader("MLflow Runs")
        mlruns_path = ROOT / "mlruns"
        if mlruns_path.exists():
            st.success(f"MLflow tracking directory: {mlruns_path}")
            st.info("Run `mlflow ui` to explore full experiment history.")
        else:
            st.info("No MLflow runs yet. Run evaluation script first.")

    st.subheader("Metric Comparison Chart")
    sample_data = pd.DataFrame(
        {
            "Metric": ["Exact Match", "BLEU", "ROUGE-L", "BERTScore", "CodeBLEU", "Syntax Validity"],
            "Score": [0.15, 0.42, 0.38, 0.71, 0.35, 0.88],
            "Dataset": ["Spider Dev"] * 6,
        }
    )
    fig = px.bar(sample_data, x="Metric", y="Score", color="Dataset", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Model Comparison")
    model_data = pd.DataFrame(
        {
            "Model": ["codegen-350M", "codegen-350M-beam", "codegen-350M"],
            "Exact Match": [0.12, 0.15, 0.10],
            "Execution Acc": [0.25, 0.30, 0.22],
            "Dataset": ["Spider", "Spider", "BIRD"],
        }
    )
    fig2 = px.bar(
        model_data,
        x="Model",
        y=["Exact Match", "Execution Acc"],
        barmode="group",
        facet_col="Dataset",
    )
    st.plotly_chart(fig2, use_container_width=True)


def main():
    st.sidebar.title("CodeGen Studio")
    st.sidebar.markdown("**Interactive Database Querying**")
    st.sidebar.markdown("Using Salesforce/codegen-350M-multi")

    page = st.sidebar.radio(
        "Navigation",
        ["Text-to-SQL", "SQL-to-NoSQL", "Interactive Querying", "Evaluation Dashboard"],
    )

    if page == "Text-to-SQL":
        page_text2sql()
    elif page == "SQL-to-NoSQL":
        page_sql2nosql()
    elif page == "Interactive Querying":
        page_interactive()
    else:
        page_evaluation()


if __name__ == "__main__":
    main()
