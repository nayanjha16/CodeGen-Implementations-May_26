"" 
# Group-30 CodeGen Application

A voice-enabled web interface for code generation using fine-tuned Qwen2.5-Coder-7B models with LoRA adapters.

## Overview

This application provides an interactive web interface that allows users to:
- **Generate Python code** from natural language descriptions (NL → Python)
- **Convert Python code to C++** (Python → C++)
- **Use voice input** for hands-free code generation
- **Automatic task routing** - the system detects whether you want to generate code or convert it

## Features

- 🎤 **Voice Input**: Speak your requirements and get code generated
- 🤖 **Dual Adapters**: Two specialized LoRA adapters on a shared base model
- ⚡ **GPU Accelerated**: Runs on Google Colab with T4/L4 GPU
- 🌐 **Web Interface**: Gradio-based UI accessible from any browser
- 🔄 **Auto Task Detection**: Automatically routes to the appropriate adapter

## Quick Start

### Option 1: Google Colab (Recommended)

1. Open `app.ipynb` in Google Colab
2. Go to **Runtime → Change runtime type → GPU** (T4 or L4)
3. Run all cells
4. Click the public URL that appears at the end

### Option 2: Local Setup

```bash
# Install dependencies
pip install gradio "peft>=0.11" "transformers>=4.44" accelerate bitsandbytes

# Run the notebook
jupyter notebook app.ipynb
```

## Architecture

```
app.ipynb
├── Cell 1: Install dependencies (gradio, peft, transformers, etc.)
├── Cell 2: Import libraries and define constants
├── Cell 3: Download LoRA adapters from GitHub LFS
├── Cell 4: Load base model (4-bit quantized) + adapters
├── Cell 5: Load Whisper for speech-to-text
├── Cell 6: Define core functions
│   ├── build_prompt() - Format chat templates
│   ├── extract_code() - Parse code from responses
│   ├── generate() - Code generation
│   ├── classify_task() - LLM-based routing
│   └── transcribe() - Audio transcription
└── Cell 7: Launch Gradio interface
```

## Usage

### Text Input
1. Type a description: "Create a function that sorts a list of numbers"
2. Select "Auto" or "NL -> Python"
3. Click "Generate"
4. View the generated Python code

### Voice Input
1. Click the microphone icon
2. Speak clearly: "Write a Python function to calculate Fibonacci numbers"
3. The audio is transcribed and code is generated

### Code Conversion
1. Paste Python code into the input box
2. Select "Python -> C++"
3. Click "Generate"
4. Get the C++ equivalent code

## Adapters

| Adapter | Purpose | Training Data |
|---------|---------|---------------|
| NL → Python | Generate Python from descriptions | Natural language → Python code pairs |
| Python → C++ | Convert Python to C++ | Python → C++ code pairs |

Both adapters are fine-tuned on Qwen/Qwen2.5-Coder-7B-Instruct using LoRA (Low-Rank Adaptation).

## Dependencies

- **Gradio** - Web UI framework
- **Transformers** - HuggingFace model library
- **PEFT** - Parameter-Efficient Fine-Tuning
- **BitsAndBytes** - 4-bit quantization
- **Whisper** - Speech recognition (openai/whisper-base)

## Environment Variables

Set the following for faster downloads (optional):

```bash
HF_TOKEN=your_huggingface_token
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "CUDA out of memory" | Reduce max_new_tokens or use smaller batch |
| "Adapter download failed" | Check internet connection, verify GitHub LFS access |
| "Whisper not loading" | Ensure GPU is available for ASR model |
| "No public URL" | Check Colab settings, try `demo.launch(share=False)` |

## File Structure

```
Application/
├── app.ipynb          # Main application notebook
├── README.md          # This file
└── (adapters downloaded at runtime)
```

## Model Details

- **Base Model**: Qwen/Qwen2.5-Coder-7B-Instruct
- **Quantization**: 4-bit (NF4) for memory efficiency
- **Adapters**: LoRA with r=16, alpha=32
- **ASR Model**: openai/whisper-base

## License

This project is part of the Group-30 CodeGen implementation.
