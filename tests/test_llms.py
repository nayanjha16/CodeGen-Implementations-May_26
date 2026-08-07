"""Tests for agent.llms model wiring and generation helpers."""

from unittest import mock

from agent.llms import _generate_with_supported_kwargs, ask_generate


def test_generate_with_supported_kwargs_filters_unknown_args():
    class StubGenerator:
        def generate(self, prompt: str, temperature: float = 0.0, response_type: str = "code"):
            return f"{prompt}|{temperature}|{response_type}"

    result = _generate_with_supported_kwargs(
        StubGenerator(),
        "hello",
        temperature=0.0,
        repetition_penalty=1.15,
        response_type="doc",
    )
    assert result == "hello|0.0|doc"


def test_ask_generate_works_without_repetition_penalty_param():
    class LegacyGenerator:
        def generate(self, prompt: str, temperature: float = 0.0, max_new_tokens: int = 512, response_type: str = "doc"):
            return f"answer:{prompt}"

    with mock.patch("agent.llms.get_ask_generator", return_value=LegacyGenerator()):
        result = ask_generate("Summarize repo")
    assert result == "answer:Summarize repo"


def test_planner_default_uses_instruct_model():
    from agent import llms

    llms._planner = None
    mock_gen = object()
    with mock.patch("agent.llms._load_side_model", return_value=mock_gen) as mock_load:
        assert llms.get_planner_generator() is mock_gen
        mock_load.assert_called_once_with(
            "ASK_PLANNER_MODEL_ID",
            "Qwen/Qwen2.5-1.5B-Instruct",
            128,
        )
    llms._planner = None


def test_planner_ft_env_reuses_codegen():
    from agent import llms

    llms._planner = None
    llms._codegen = object()
    with mock.patch.dict("os.environ", {"ASK_PLANNER_MODEL_ID": "ft"}), mock.patch(
        "agent.llms.get_codegen_generator", return_value=llms._codegen
    ) as mock_codegen:
        assert llms.get_planner_generator() is llms._codegen
        mock_codegen.assert_called_once()
    llms._planner = None
    llms._codegen = None


def test_ask_default_uses_instruct_model():
    from agent import llms

    llms._ask = None
    with mock.patch("generator.CodeGenerator") as mock_cls:
        mock_cls.return_value = object()
        llms.get_ask_generator()
        mock_cls.assert_called_once_with(
            model_path="Qwen/Qwen2.5-1.5B-Instruct",
            temperature=0.0,
            max_new_tokens=512,
        )
    llms._ask = None


def test_ask_generator_is_cached():
    from agent import llms

    llms._ask = None
    sentinel = object()
    with mock.patch("generator.CodeGenerator", return_value=sentinel) as mock_cls:
        first = llms.get_ask_generator()
        second = llms.get_ask_generator()
        assert first is second is sentinel
        mock_cls.assert_called_once()
    llms._ask = None


def test_set_ask_generator_injects_instance():
    from agent import llms

    injected = object()
    llms.set_ask_generator(injected)
    assert llms.get_ask_generator() is injected
    llms._ask = None
