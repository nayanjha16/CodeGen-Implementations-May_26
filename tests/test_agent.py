"""Tests for LangGraph agent (mocked models — no GPU required)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestAgentState:
    def test_initial_state_defaults_function_unit(self):
        from agent.state import initial_state

        s = initial_state("print hello")
        assert s["unit"] == "function"
        assert s["input_type"] == "nl"
        assert s["max_retries"] == 3

    def test_initial_state_java_route(self):
        from agent.state import initial_state

        s = initial_state("", java_code="class A {}")
        assert s["input_type"] == "java"

    def test_initial_state_pseudocode(self):
        from agent.state import initial_state

        s = initial_state("Algorithm: Foo\nBegin\n  End if\n")
        assert s["input_type"] == "pseudocode"

    def test_unit_class_supported(self):
        from agent.state import initial_state

        s = initial_state("Singleton logger", unit="class", pattern="Singleton")
        assert s["unit"] == "class"
        assert s["pattern"] == "Singleton"


class TestPrompts:
    def test_parse_judge_yes(self):
        from agent.prompts import parse_judge_response

        yes, reason = parse_judge_response("YES\nLooks correct")
        assert yes is True
        assert "correct" in reason.lower() or reason

    def test_parse_judge_no(self):
        from agent.prompts import parse_judge_response

        yes, reason = parse_judge_response("NO — wrong output")
        assert yes is False


class TestTools:
    def test_run_python_ok(self):
        from agent.tools import run_python_dict

        result = run_python_dict("print(2 + 3)")
        assert result["passed"] is True
        assert "5" in result["stdout"]

    def test_parse_ast_functions(self):
        from agent.tools import parse_ast

        summary = parse_ast.invoke({"code": "def add(a,b):\n    return a+b\n", "language": "python"})
        assert "add" in summary


class TestGraphMocked:
    def test_solve_happy_path_with_fix_loop(self):
        from agent.graph import reset_agent_graph, solve
        from agent.llms import set_codegen_generator, set_judge_generator

        reset_agent_graph()

        codegen = MagicMock()
        # NL→Java, Java→Python (broken), then Fix → good
        codegen.generate.side_effect = [
            "public class Main { public static void main(String[] a){ System.out.println(5);} }",
            "print(2 +",  # syntax error
            "print(2 + 3)",  # fixed
        ]
        judge = MagicMock()
        judge.generate.return_value = "YES\nPrinted 5 as requested"

        set_codegen_generator(codegen)
        set_judge_generator(judge)

        result = solve(
            "Write a program that prints the sum of 2 and 3.",
            max_retries=3,
            unit="function",
        )
        assert result["judge_yes"] is True
        assert result["attempts"] >= 1
        assert "print" in result["python_code"]
        steps = [t["step"] for t in result["trace"]]
        assert "nl_to_java" in steps
        assert "java_to_python" in steps
        assert "execute" in steps
        assert "judge" in steps
        assert "fix_python" in steps

    def test_router_pl_to_pl(self):
        from agent.graph import reset_agent_graph, solve
        from agent.llms import set_codegen_generator, set_judge_generator

        reset_agent_graph()
        codegen = MagicMock()
        codegen.generate.return_value = "print(5)"
        judge = MagicMock()
        set_codegen_generator(codegen)
        set_judge_generator(judge)

        result = solve(
            "",
            java_code="System.out.println(5);",
            input_type="java",
            max_retries=1,
        )
        assert result["route"] == "pl_to_pl"
        assert result["exit_code"] == 0 or result["judge_yes"] is True or result["attempts"] >= 1

    def test_pattern_sets_class_unit(self):
        from agent.graph import reset_agent_graph, solve
        from agent.llms import set_codegen_generator, set_judge_generator

        reset_agent_graph()
        codegen = MagicMock()
        codegen.generate.side_effect = [
            "public class Logger { }",
            "class Logger:\n    pass\n",
        ]
        judge = MagicMock()
        judge.generate.return_value = "YES"
        set_codegen_generator(codegen)
        set_judge_generator(judge)

        result = solve(
            "Singleton logger",
            pattern="Singleton",
            unit="class",
            max_retries=1,
        )
        assert result["route"] == "pattern"
        assert result["unit"] == "class"


class TestProblemPack:
    def test_load_pack_has_a_through_f(self):
        from agent.problems import load_problem_pack

        pack = load_problem_pack()
        ids = {p["id"] for p in pack}
        assert "A_add_two_numbers" in ids
        assert "D_singleton_logger" in ids
        assert "F_repo_aware_helper" in ids
        singleton = next(p for p in pack if p["id"] == "D_singleton_logger")
        assert singleton["unit"] == "class"


class TestAgentAPI:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient

        with patch("api.load_generator") as mock_load, patch("api.RAGPipeline"):
            mock_gen = MagicMock()
            mock_gen.generate.return_value = "print(5)"
            mock_gen.model_path = "models/qwen_multitask/merged"
            mock_load.return_value = mock_gen

            from api import app, _generators
            import api as api_module

            for task in ("nl2py", "java2py", "code2doc", "comments", "nl2java2py"):
                _generators[task] = mock_gen
            api_module._generator = mock_gen
            api_module._model_path = "models/qwen_multitask/merged"
            api_module._agent_ready = True

            with patch("agent.graph.solve") as mock_solve:
                mock_solve.return_value = {
                    "nl_prompt": "print sum of 2 and 3",
                    "java_code": "class M {}",
                    "python_code": "print(5)",
                    "stdout": "5\n",
                    "stderr": "",
                    "judge_yes": True,
                    "judge_reason": "YES",
                    "attempts": 1,
                    "unit": "function",
                    "route": "text_to_pl",
                    "trace": [{"step": "judge", "detail": "True"}],
                }
                with TestClient(app, raise_server_exceptions=False) as c:
                    yield c, mock_solve

    def test_health_includes_agent_ready(self, client):
        c, _ = client
        resp = c.get("/health")
        assert resp.status_code == 200
        assert "agent_ready" in resp.json()

    def test_agent_solve_endpoint(self, client):
        c, mock_solve = client
        resp = c.post(
            "/agent/solve",
            json={"prompt": "print the sum of 2 and 3", "unit": "function", "max_retries": 2},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["task"] == "agent_solve"
        assert data["judge_yes"] is True
        assert data["unit"] == "function"
        mock_solve.assert_called_once()

    def test_agent_problems_endpoint(self, client):
        c, _ = client
        resp = c.get("/agent/problems")
        assert resp.status_code == 200
        assert len(resp.json()["problems"]) >= 5

    def test_agent_solve_empty(self, client):
        c, _ = client
        resp = c.post("/agent/solve", json={"prompt": "", "java_code": ""})
        assert resp.status_code == 400


class TestUIRunners:
    def test_run_generate_agent(self):
        from agent.llms import set_codegen_generator
        from agent.ui_runners import run_generate_agent

        codegen = MagicMock()
        codegen.generate.side_effect = [
            "public class Main { }",
            "print(5)",
        ]
        set_codegen_generator(codegen)
        out = run_generate_agent("print the sum of 2 and 3", unit="function")
        assert out["task"] == "agent_generate"
        assert out["java_code"]
        assert out["python_code"] == "print(5)"
        steps = [t["step"] for t in out["trace"]]
        assert "nl_to_java" in steps
        assert "java_to_python" in steps
        assert "execute" not in steps
        assert codegen.generate.call_count == 2

    def test_run_fix_agent(self):
        from agent.llms import set_codegen_generator
        from agent.ui_runners import run_fix_agent

        codegen = MagicMock()
        codegen.generate.return_value = "print(2 + 3)"
        set_codegen_generator(codegen)
        out = run_fix_agent(
            "print the sum of 2 and 3",
            "print(2 +",
            runtime="SyntaxError: '(' was never closed",
        )
        assert out["task"] == "agent_fix"
        assert "print" in out["python_code"]
        assert out["ast_info"]
        assert "Before fix:" in out["ast_info"]
        assert "After fix:" in out["ast_info"]
        assert "SyntaxError" in out["ast_info"]
        steps = [t["step"] for t in out["trace"]]
        assert "parse_ast" in steps
        assert "fix_python" in steps


class TestGenerateFixAPI:
    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient

        with patch("api.load_generator") as mock_load, patch("api.RAGPipeline"):
            mock_gen = MagicMock()
            mock_gen.generate.return_value = "print(5)"
            mock_gen.model_path = "models/qwen_multitask/merged"
            mock_load.return_value = mock_gen

            from api import app, _generators
            import api as api_module

            for task in ("nl2py", "java2py", "code2doc", "comments", "nl2java2py"):
                _generators[task] = mock_gen
            api_module._generator = mock_gen
            api_module._agent_ready = True

            with patch("agent.ui_runners.run_generate_agent") as mock_gen_agent, patch(
                "agent.ui_runners.run_fix_agent"
            ) as mock_fix_agent:
                mock_gen_agent.return_value = {
                    "prompt": "p",
                    "java_code": "class M {}",
                    "python_code": "print(5)",
                    "unit": "function",
                    "route": "text_to_pl",
                    "trace": [{"step": "nl_to_java"}],
                    "task": "agent_generate",
                }
                mock_fix_agent.return_value = {
                    "prompt": "p",
                    "python_code": "print(5)",
                    "ast_info": "functions=['main']",
                    "unit": "function",
                    "runtime": "err",
                    "trace": [{"step": "fix_python"}],
                    "task": "agent_fix",
                }
                with TestClient(app, raise_server_exceptions=False) as c:
                    yield c, mock_gen_agent, mock_fix_agent

    def test_agent_generate_endpoint(self, client):
        c, mock_gen, _ = client
        resp = c.post("/agent/generate", json={"prompt": "print 5", "unit": "function"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["task"] == "agent_generate"
        assert data["python_code"] == "print(5)"
        mock_gen.assert_called_once()

    def test_agent_generate_empty(self, client):
        c, _, _ = client
        resp = c.post("/agent/generate", json={"prompt": "  "})
        assert resp.status_code == 400

    def test_agent_fix_endpoint(self, client):
        c, _, mock_fix = client
        resp = c.post(
            "/agent/fix",
            json={
                "prompt": "print 5",
                "python_code": "print(2 +",
                "runtime": "SyntaxError",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["task"] == "agent_fix"
        assert data["python_code"] == "print(5)"
        mock_fix.assert_called_once()

    def test_agent_fix_empty_code(self, client):
        c, _, _ = client
        resp = c.post("/agent/fix", json={"prompt": "x", "python_code": ""})
        assert resp.status_code == 400
