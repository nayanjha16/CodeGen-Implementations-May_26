from typing import Any, Optional, Dict, Tuple
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
import torch

from config import STARCODER_BASE_MODEL, QWEN_BASE_MODEL, HF_TOKEN

_models: Dict[str, Tuple[Any, Any]] = {}


def get_model(model_id: str, adapter_path: Optional[str] = None, quant_config: Optional[BitsAndBytesConfig] = None) -> Tuple[Any, Any]:
    """Load and cache a tokenizer+model pair for `model_id`.

    - `adapter_path` can be a PEFT adapter directory (LoRA) to load on top of the base model.
    - `quant_config` can be provided for quantized loads (e.g. BitsAndBytesConfig).

    Returns (tokenizer, model).
    """
    key = f"{model_id}"
    if key in _models:
        return _models[key]

    tokenizer = AutoTokenizer.from_pretrained(model_id, token=HF_TOKEN)

    load_kwargs: Dict[str, Any] = dict(device_map="auto", torch_dtype=torch.float16, low_cpu_mem_usage=True)
    if quant_config is not None:
        load_kwargs["quantization_config"] = quant_config

    base_model = AutoModelForCausalLM.from_pretrained(model_id, token=HF_TOKEN, **load_kwargs)

    if adapter_path:
        model = PeftModel.from_pretrained(base_model, adapter_path)
    else:
        model = base_model

    _models[key] = (tokenizer, model)
    return tokenizer, model


def get_starcoder() -> Tuple[Any, Any]:
    bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    llm_int8_enable_fp32_cpu_offload=True,
    )
    adapter_path = "./model/starcoder2-python-java-custom-lora"

    return get_model(STARCODER_BASE_MODEL, adapter_path=adapter_path, quant_config=bnb_config)


# def get_qwen() -> Tuple[Any, Any]:
#     bnb_config = BitsAndBytesConfig(
#     load_in_4bit=True,
#     bnb_4bit_compute_dtype=torch.bfloat16,
#     bnb_4bit_quant_type="nf4",
#     bnb_4bit_use_double_quant=True,
#     llm_int8_enable_fp32_cpu_offload=True,
#     )
#     adapter_path = ""

#     return get_model(QWEN_BASE_MODEL, adapter_path=adapter_path, quant_config=bnb_config)
