# CodeGen Backend

A FastAPI-based code generation backend that serves code generation, translation, and repair endpoints using a fine-tuned StarCoder2-3B model with a PEFT LoRA adapter.

## Project Overview

This project exposes the following API routes:

- `POST /generate` — generate code from an instruction prompt
- `POST /translate` — translate code from one language to another
- `POST /repair` — repair or regenerate code based on a problem statement

The backend loads the tokenizer and model at startup through the model loader and uses Hugging Face authentication and API keys from environment configuration.

## Prerequisites

- Python 3.10+
- Windows PowerShell or Git Bash
- Access to Hugging Face token (`HF_TOKEN`)

## Setup Instructions

### 1. Create and activate a virtual environment

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script activation, run this once in the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root with the following values:

```env
HF_TOKEN=your_huggingface_token
STARCODER_BASE_MODEL=bigcode/starcoder2-3b
```

### 4. Run the backend

```bash
python app.py
```

The API will start on:

- `http://localhost:8000`

## Google Colab + Ngrok Exposure

Use the following steps when you want to expose the FastAPI StarCoder backend in Google Colab through a public ngrok URL.

### 1. Open the notebook in Colab

Upload or open the notebook `Fast_API_Starcoder_Finetuned.ipynb` in Google Colab.

### 2. Install the required Python packages

```python
!pip install -r requirements.txt
!pip install pyngrok
```

### 3. Set the required environment variables

```python
import os
os.environ["HF_TOKEN"] = "your_huggingface_token"
os.environ["STARCODER_BASE_MODEL"] = "bigcode/starcoder2-3b"
os.environ["NGROK_AUTH_TOKEN"] = "your_ngrok_auth_token"
```

You must have a valid ngrok authentication token to create a public tunnel from Colab.

### 4. Start the FastAPI app on a public port

```python
!python app.py
```

If you are running inside Colab, start the server with a fixed host and port using Uvicorn:

```python
!uvicorn app:app --host 0.0.0.0 --port 8000
```

### 5. Expose the app with ngrok

```python
from pyngrok import ngrok

ngrok.set_auth_token(os.environ["NGROK_AUTH_TOKEN"])
public_url = ngrok.connect(8000)
print(public_url)
```

### 6. Access the API through the ngrok URL

Once the tunnel is active, your API endpoints will be available through a public URL similar to:

```text
https://<random-subdomain>.ngrok-free.app/generate
```

You can call the endpoints using the public URL instead of `localhost`.

## Notes

- The local LoRA adapter is expected to be present in the `model/starcoder2-python-java-custom-lora` directory.
- The Hugging Face credentials are required for the application to start successfully.
- The project is designed for local development and inference workflows using the model adapter packaged in this repository.
