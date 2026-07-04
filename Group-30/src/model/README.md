# Group-30 CodeGen Fine-Tuned Models

This folder contains the LoRA adapters for the fine-tuned Qwen2.5-Coder-7B model.

## Contents

| File | Size | Description |
|------|------|-------------|
| `Qwen_NL_to_PL_LORA_Adapter.zip` | ~150 MB | LoRA adapter for Natural Language → Python code generation |
| `Qwen_Python_to_CPP_LORA_Adapter.zip` | ~150 MB | LoRA adapter for Python → C++ code conversion |

## Training Dataset

The adapters were fine-tuned on a dataset split into three equal parts:

| Phase | Records | Purpose |
|-------|---------|---------|
| Baseline | `num_records // 3` | Used for baseline accuracy computation |
| LORA Training | `num_records // 3` | Used for LoRA adapter fine-tuning |
| LORA Validation | `num_records // 3` | Used for validation of fine-tuned models |

**Note:** The `num_records` value is passed as a command-line argument to the training script and is not encoded in the adapter filenames.

## Model Architecture

- **Base Model**: Qwen/Qwen2.5-Coder-7B-Instruct
- **Fine-tuning Method**: LoRA (Low-Rank Adaptation)
- **LoRA Configuration**: r=16, alpha=32
- **Quantization**: 4-bit (NF4) for inference efficiency

## Usage

These adapters are loaded by the application in `app.ipynb`:

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM

# Load base model (4-bit quantized)
base = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-Coder-7B-Instruct",
    device_map="auto",
    quantization_config=bnb_config
)

# Load the NL → Python adapter
model = PeftModel.from_pretrained(
    base, 
    "/path/to/Qwen_NL_to_PL_LORA_Adapter",
    adapter_name="NL -> Python"
)

# Switch to Python → C++ adapter
model.load_adapter(
    "/path/to/Qwen_Python_to_CPP_LORA_Adapter",
    adapter_name="Python -> C++"
)
model.set_adapter("Python -> C++")
```

## Download

The adapters are stored using Git LFS. When cloning the repository:

```bash
git lfs install
git clone <repository-url>
```

Or download directly from GitHub:

```
https://media.githubusercontent.com/media/{REPO}/{BRANCH}/Group-30/src/model/{ADAPTER_NAME}.zip
```

## File Structure (Inside Each Zip)

```
{Adapter_Name}.zip
└── {Adapter_Name}/
    ├── adapter_config.json      # LoRA configuration
    ├── adapter_model.safetensors  # LoRA weights
    └── README.md                # Adapter-specific documentation
```

**Note:** Tokenizer files are NOT included in the adapter zip. The application uses the tokenizer from the base Qwen/Qwen2.5-Coder-7B-Instruct model.

## Related Files

- **Training Code**: `../Training/codegen_30.py`
- **Application**: `../Application/app.ipynb`
- **Architecture Diagrams**: `../../Architecture/Diagrams.md`
