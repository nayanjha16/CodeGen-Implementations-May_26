from __future__ import annotations

from codegen_rag.models.generation_config import GenerationConfig
from codegen_rag.tasks.code_translation import CodeTranslationTask
from codegen_rag.tasks.commit_message_generation import CommitMessageGenerationTask
from codegen_rag.tasks.documentation_generation import DocumentationGenerationTask
from codegen_rag.tasks.program_synthesis import ProgramSynthesisTask


def test_program_synthesis_prompt_contains_intent(fake_model):
    task = ProgramSynthesisTask(fake_model, GenerationConfig(), language="python")
    prompt = task.build_prompt({"intent": "reverse a string"})
    assert "reverse a string" in prompt


def test_program_synthesis_postprocess_cuts_at_stop_marker(fake_model):
    task = ProgramSynthesisTask(fake_model)
    raw = "def f():\n    return 1\nclass Unrelated:\n    pass"
    cleaned = task.postprocess(raw)
    assert "class Unrelated" not in cleaned
    assert "def f()" in cleaned


def test_program_synthesis_run_returns_prediction(fake_model, sample_codocbench_record):
    task = ProgramSynthesisTask(fake_model)
    result = task.run(sample_codocbench_record)
    assert result["task"] == "program_synthesis"
    assert result["prediction"] == fake_model.canned_completion.strip()


def test_documentation_task_prompt_includes_code(fake_model, sample_codocbench_record):
    task = DocumentationGenerationTask(fake_model)
    prompt = task.build_prompt(sample_codocbench_record)
    assert sample_codocbench_record["code"] in prompt


def test_documentation_task_postprocess_trims_at_closing_quotes(fake_model):
    task = DocumentationGenerationTask(fake_model)
    raw = 'Adds two numbers.\n"""\nsome trailing garbage'
    cleaned = task.postprocess(raw)
    assert cleaned == "Adds two numbers."


def test_commit_message_task_truncates_long_diff(fake_model, sample_codocbench_record):
    task = CommitMessageGenerationTask(fake_model)
    big_record = {**sample_codocbench_record, "commit_diff": "x" * 5000}
    prompt = task.build_prompt(big_record)
    assert len(prompt) < 3100


def test_commit_message_postprocess_single_line():
    task = CommitMessageGenerationTask(model=None)  # postprocess doesn't need the model
    result = task.postprocess("Fix bug in parser\n\nLonger explanation body here")
    assert result == "Fix bug in parser"


def test_code_translation_prompt_mentions_languages(fake_model):
    task = CodeTranslationTask(fake_model, source_language="python", target_language="java")
    prompt = task.build_prompt({"code": "def f(): pass"})
    assert "python" in prompt
    assert "java" in prompt


def test_run_batch_processes_all_records(fake_model, sample_codocbench_record):
    task = ProgramSynthesisTask(fake_model)
    results = task.run_batch([sample_codocbench_record] * 3)
    assert len(results) == 3
    assert len(fake_model.calls) == 3
