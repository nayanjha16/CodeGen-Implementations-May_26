"""Mentor-facing Gradio interface shared with the deployable FastAPI UI."""

from __future__ import annotations

from typing import Optional

from src.demo_showcases import MINIMUM_EXAMPLES_PER_SECTION, showcase_examples
from src.generation_validation import GenerationOutputValidator
from src.registry import TaskRegistry
from src.repository_catalog import repository_catalog


def build_gradio_showcase(
    gen_engine,
    baseline_model,
    baseline_tokenizer,
    finetuned_model=None,
    finetuned_tokenizer=None,
    retrieval_engine=None,
    retrieval_engines=None,
    task_registry: Optional[TaskRegistry] = None,
    output_validator: Optional[GenerationOutputValidator] = None,
    project_root=None,
):
    """Build a controlled four-arm UI without loading any model twice."""

    import gradio as gr

    registry = task_registry or TaskRegistry()
    validator = output_validator or GenerationOutputValidator(gen_engine.config)
    engines = dict(retrieval_engines or {})
    if retrieval_engine is not None and "ledgerflow" not in engines:
        engines["ledgerflow"] = retrieval_engine

    tasks = registry.all_tasks()
    task_labels = [
        f"{task_id}: {row['source']} -> {row['target']}"
        for task_id, row in tasks.items()
    ]
    task_by_label = dict(zip(task_labels, tasks))
    label_by_task = {value: key for key, value in task_by_label.items()}

    repos = repository_catalog()
    repo_labels = [row["title"] for row in repos]
    repo_by_label = {row["title"]: row for row in repos}
    examples = showcase_examples(project_root)

    def example_label(row):
        return f"{row['task_id']} | {row['title']}"

    def filtered(repo_id, task_id):
        rows = [
            row
            for row in examples
            if row["repository_id"] == repo_id
            and row["task_id"] == task_id
        ]
        if len(rows) < MINIMUM_EXAMPLES_PER_SECTION:
            raise RuntimeError(
                f"{repo_id}/{task_id} has {len(rows)} examples; "
                f"at least {MINIMUM_EXAMPLES_PER_SECTION} are required."
            )
        return rows

    # Fail early while building the UI rather than presenting an empty menu.
    for repo in repos:
        for task_id in tasks:
            filtered(repo["repository_id"], task_id)

    def _note(row):
        expected = ", ".join(
            f"`{name}`" for name in row["expected_sources"]
        ) or "none"
        actual = (
            f"  \n**Actual source:** `{row['source_path']}`"
            if row.get("source_path")
            else ""
        )
        return (
            f"**{row['capability']}** - {row['description']}  \n"
            f"**Expected evidence:** {expected}{actual}"
        )

    def apply_repo(repo_label):
        repo = repo_by_label[repo_label]
        task_id = "T1"
        rows = filtered(repo["repository_id"], task_id)
        values = [example_label(row) for row in rows]
        first = rows[0]
        rag_values = (
            ["No RAG", "With RAG"]
            if repo["repository_id"] in engines
            else ["No RAG"]
        )
        return (
            label_by_task[task_id],
            gr.update(choices=values, value=values[0]),
            first["input_text"],
            gr.update(value=rag_values),
            repo["description"],
            _note(first),
        )

    def apply_task(repo_label, task_label):
        repo_id = repo_by_label[repo_label]["repository_id"]
        rows = filtered(repo_id, task_by_label[task_label])
        values = [example_label(row) for row in rows]
        first = rows[0]
        return (
            gr.update(choices=values, value=values[0]),
            first["input_text"],
            _note(first),
        )

    def apply_example(repo_label, example):
        repo_id = repo_by_label[repo_label]["repository_id"]
        row = next(
            item
            for item in examples
            if item["repository_id"] == repo_id
            and example_label(item) == example
        )
        return label_by_task[row["task_id"]], row["input_text"], _note(row)

    def _reason_text(validation):
        reason = (
            validation.get("reason")
            or validation.get("compiler_stderr")
            or ""
        )
        return (
            str(reason)
            .replace("\n", " ")
            .replace("`", "'")
            .strip()[:280]
        )

    def status(validation, *, retried=False, first_reason=""):
        state = validation.get("status", "UNKNOWN")
        reason = _reason_text(validation)
        if retried and validation.get("valid"):
            detail = first_reason or "first attempt was structurally invalid"
            return f"**PASS AFTER VALIDATED RETRY** `{detail}`"
        return f"**{state}**" + (f" `{reason}`" if reason else "")

    def retry_requirement(task_id):
        if task_id in {"T1", "T4"}:
            return (
                "\n\nCorrection requirement: Return syntactically valid multi-line "
                "Python code only. Put imports and each def or class statement on "
                "separate lines. Never place def or class after a semicolon."
            )
        if task_id in {"T2", "T3"}:
            return (
                "\n\nCorrection requirement: Return one complete compilable Java "
                "class only, with balanced braces and no Markdown fences."
            )
        return (
            "\n\nCorrection requirement: Return a concise plain-language "
            "explanation only, without Markdown code fences."
        )

    def structural_effect(before, after, label):
        if before is None or after is None:
            return f"- **{label}:** not evaluated"
        before_valid = bool(before.get("valid"))
        after_valid = bool(after.get("valid"))
        if not before_valid and after_valid:
            result = "structural improvement (FAIL -> PASS)"
        elif before_valid and not after_valid:
            result = "structural regression (PASS -> FAIL)"
        elif before_valid and after_valid:
            result = "both structurally valid; inspect correctness/content"
        else:
            result = "both structurally invalid"
        return f"- **{label}:** {result}"

    def run(
        repo_label,
        task_label,
        input_text,
        model_choices,
        rag_choices,
        retry_invalid,
    ):
        repo_id = repo_by_label[repo_label]["repository_id"]
        task_id = task_by_label[task_label]
        instruction = gen_engine.prompt_builder.build_instruction(task_id)

        context = ""
        sources = []
        decision_note = "RAG not requested."
        if "With RAG" in rag_choices:
            engine = engines.get(repo_id)
            if engine is None:
                decision_note = (
                    "RAG requested, but this repository index is unavailable."
                )
            else:
                # A repository is explicitly selected in this UI. Keep the
                # small model grounded on the single best repository symbol;
                # generic corpus examples are evaluated through the separate
                # corpus-RAG path and would be distractors here.
                outcome = engine.resolve(
                    input_text or "",
                    task_id=task_id,
                    top_k=1,
                    sources=("repo",),
                )
                context = outcome.context
                sources = outcome.sources
                decision = outcome.decision
                decision_note = (
                    f"decision={decision.reason} | used={outcome.used} | "
                    f"top={decision.top_score:.3f} | "
                    f"margin={decision.score_margin:.3f}"
                )

        lookup = {
            "Baseline": (baseline_model, baseline_tokenizer),
            "Fine-tuned": (finetuned_model, finetuned_tokenizer),
        }
        keys = ("baseline_no", "baseline_rag", "fine_no", "fine_rag")
        outputs = {key: "" for key in keys}
        statuses = {key: "_Not run_" for key in keys}
        validations = {key: None for key in keys}

        for model_name, prefix in (
            ("Baseline", "baseline"),
            ("Fine-tuned", "fine"),
        ):
            if model_name not in model_choices:
                continue
            model, tokenizer = lookup[model_name]
            if model is None:
                statuses[f"{prefix}_no"] = "_Model unavailable_"
                statuses[f"{prefix}_rag"] = "_Model unavailable_"
                continue

            for rag_label, suffix in (
                ("No RAG", "no"),
                ("With RAG", "rag"),
            ):
                if rag_label not in rag_choices:
                    continue

                key = f"{prefix}_{suffix}"
                arm_context = context if suffix == "rag" else ""
                raw = gen_engine.generate(
                    model,
                    tokenizer,
                    instruction,
                    input_text or "",
                    task_id=task_id,
                    retrieved_context=arm_context,
                )
                checked = validator.validate(task_id, raw)
                retried = False
                first_reason = _reason_text(checked)

                # UI-only reliability policy. Evaluation artifacts remain the
                # untouched one-generation experiments; a retry is explicitly
                # labelled and never silently represented as the first output.
                if retry_invalid and not checked.get("valid"):
                    retry_raw = gen_engine.generate(
                        model,
                        tokenizer,
                        instruction,
                        (input_text or "") + retry_requirement(task_id),
                        task_id=task_id,
                        retrieved_context=arm_context,
                    )
                    retry_checked = validator.validate(task_id, retry_raw)
                    if retry_checked.get("valid"):
                        raw = retry_raw
                        checked = retry_checked
                        retried = True

                outputs[key] = checked.get("normalized_output", raw)
                validations[key] = checked
                statuses[key] = status(
                    checked,
                    retried=retried,
                    first_reason=first_reason,
                )

        comparison_lines = [
            "### Honest structural comparison",
            structural_effect(
                validations["baseline_no"],
                validations["fine_no"],
                "Fine-tuning effect without RAG",
            ),
            structural_effect(
                validations["baseline_rag"],
                validations["fine_rag"],
                "Fine-tuning effect with RAG",
            ),
            structural_effect(
                validations["baseline_no"],
                validations["baseline_rag"],
                "RAG effect on baseline",
            ),
            structural_effect(
                validations["fine_no"],
                validations["fine_rag"],
                "RAG effect on fine-tuned model",
            ),
            "",
            "Structural PASS does not prove semantic correctness; use the "
            "retrieval trace and saved evaluation reports for the mentor claim.",
        ]

        evidence_lines = [f"**RAG decision:** {decision_note}"]
        for source in sources:
            evidence_lines.append(
                f"- **#{source.get('rank', '?')} "
                f"`{str(source.get('name', 'unknown'))}`** - "
                f"`{str(source.get('file_path', ''))}`  \n"
                f"  score={source.get('score')} | "
                f"dense={source.get('dense_score')} | "
                f"lexical={source.get('lexical_score')} | "
                f"reranker={source.get('reranker_score')} | "
                f"method={source.get('retrieval_method')} | "
                f"provenance={source.get('provenance')}"
            )

        return (
            tuple(outputs[key] for key in keys)
            + tuple(statuses[key] for key in keys)
            + ("\n".join(comparison_lines), "\n".join(evidence_lines))
        )

    # LedgerFlow/T1 is the strongest repository-grounded starting point.
    first_repo = next(
        repo for repo in repos if repo["repository_id"] == "ledgerflow"
    )
    first_rows = filtered(first_repo["repository_id"], "T1")
    first = first_rows[0]
    first_choices = [example_label(row) for row in first_rows]

    with gr.Blocks(
        title="RepoCoder Studio",
        theme=gr.themes.Soft(primary_hue="indigo"),
    ) as demo:
        gr.Markdown(
            "# RepoCoder Studio\n"
            "**Baseline/fine-tuned x no-RAG/RAG**, with the same input and "
            "shared retrieval evidence. Every repository/task section has at "
            "least three preloaded examples."
        )

        with gr.Row():
            repo_dropdown = gr.Dropdown(
                repo_labels,
                value=first_repo["title"],
                label="Repository context",
            )
            task_dropdown = gr.Dropdown(
                task_labels,
                value=label_by_task["T1"],
                label="Task contract",
            )
            example_dropdown = gr.Dropdown(
                first_choices,
                value=first_choices[0],
                label="Preloaded examples (minimum 3 per section)",
            )

        repo_note = gr.Markdown(first_repo["description"])
        example_note = gr.Markdown(_note(first))
        input_box = gr.Textbox(
            value=first["input_text"],
            lines=12,
            label="Input",
        )

        with gr.Row():
            models = gr.CheckboxGroup(
                ["Baseline", "Fine-tuned"],
                value=["Baseline"]
                + (["Fine-tuned"] if finetuned_model is not None else []),
                label="Models",
            )
            rag_modes = gr.CheckboxGroup(
                ["No RAG", "With RAG"],
                value=["No RAG", "With RAG"]
                if "ledgerflow" in engines
                else ["No RAG"],
                label="Evidence modes",
            )
            retry_invalid = gr.Checkbox(
                value=True,
                label="Retry once if structurally invalid",
                info="Retries are visibly labelled and are UI-only.",
            )

        run_button = gr.Button(
            "Run controlled comparison",
            variant="primary",
        )

        output_components = []
        status_components = []
        with gr.Row():
            for title in (
                "Baseline / No RAG",
                "Baseline / With RAG",
            ):
                with gr.Column():
                    gr.Markdown(f"### {title}")
                    status_components.append(gr.Markdown("_Not run_"))
                    output_components.append(
                        gr.Code(label="Validated output", lines=16)
                    )
        with gr.Row():
            for title in (
                "Fine-tuned / No RAG",
                "Fine-tuned / With RAG",
            ):
                with gr.Column():
                    gr.Markdown(f"### {title}")
                    status_components.append(gr.Markdown("_Not run_"))
                    output_components.append(
                        gr.Code(label="Validated output", lines=16)
                    )

        comparison = gr.Markdown()
        with gr.Accordion("Retrieval trace and provenance", open=True):
            evidence = gr.Markdown()

        repo_dropdown.change(
            apply_repo,
            [repo_dropdown],
            [
                task_dropdown,
                example_dropdown,
                input_box,
                rag_modes,
                repo_note,
                example_note,
            ],
        )
        task_dropdown.change(
            apply_task,
            [repo_dropdown, task_dropdown],
            [example_dropdown, input_box, example_note],
        )
        example_dropdown.change(
            apply_example,
            [repo_dropdown, example_dropdown],
            [task_dropdown, input_box, example_note],
        )
        run_button.click(
            run,
            [
                repo_dropdown,
                task_dropdown,
                input_box,
                models,
                rag_modes,
                retry_invalid,
            ],
            output_components
            + status_components
            + [comparison, evidence],
        )

    return demo
