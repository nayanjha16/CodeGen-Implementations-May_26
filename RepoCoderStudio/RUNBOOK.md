# RepoCoder Studio — Reproduction, Demonstration and Deployment Runbook

This is the detailed operator guide for the final Stage 5 submission. It uses
two notebooks in a deliberate sequence:

1. `notebooks/RepoCoderStudio_Fast_Corrected_Retrain.ipynb` builds and evaluates
   the corrected Combined Stage, Stage 4 and original Stage 5 pipeline.
2. `notebooks/RepoCoderStudio_RAG_Augmented_Retrain.ipynb` consumes those saved
   artifacts and creates the final grounded RAG-aware v1.2 adapter.

The packaged outputs allow review, UI launch and deployment without retraining.
Only use the complete fresh-run path when you intentionally want to reproduce
every result.

# Part A — Put the project in the correct place

1. Extract or upload the complete `RepoCoderStudio` folder.
2. For Colab, its exact Drive path must be:

   ```text
   /content/drive/MyDrive/RepoCoderStudio
   ```

3. Confirm that `src`, `app`, `scripts`, `notebooks`, `outputs` and
   `repo_explorer_data` are immediately inside it. A path such as
   `RepoCoderStudio/RepoCoderStudio/src` is wrong.
4. If Drive creates filenames such as `artifact_manifest (1).py`, delete the
   duplicate and retain the exact canonical filename `artifact_manifest.py`.
   Python imports require exact filenames.
5. Do not combine this folder with an older recovery ZIP. The submitted
   adapters, manifests and indexes are fingerprinted and must remain together.

# Part B — Review without running expensive cells

No GPU is required for this path.

1. Read `RepoCoderStudio_Implementation_Report.md` (one level up from this folder).
2. Inspect both executed notebooks in the order listed above.
3. Inspect `outputs/evaluation` and `outputs/reports`.
4. Confirm that
   `outputs/reports/rag_grounded_retrain_v1_2_verification.json` has
   `overall_success: true`.
5. Confirm that the final adapter folder contains both
   `adapter_model.safetensors` and `trained_model_manifest.json`:

   ```text
   outputs/adapters/RepoCoderStudio_RAGAware_LoRA_v1_2/
   ```

# Part C — Complete fresh Colab reproduction

Use a T4 GPU. Colab availability and runtime limits are external constraints;
all durable artifacts are written to Google Drive.

## Step 1 — Run the corrected full-run notebook

1. Open `notebooks/RepoCoderStudio_Fast_Corrected_Retrain.ipynb` in Colab.
2. Choose **Runtime → Change runtime type → T4 GPU**.
3. Run Cell 0, `Install and Validate Dependencies`, once.
4. Wait for `INSTALLATION VALIDATED`.
5. Restart the session when instructed. Do not delete the runtime.
6. Continue at Cell 0B, `Environment Verification — run after restarting`.
   Do not skip Cell 0B and do not rerun Cell 0 after the restart.
7. In Project Initialization, confirm:

   ```text
   run mode: demo
   train/validation/test source limits: 300/60/60
   evaluation examples per task: 20
   learning rate: 5e-5
   adapter: RepoCoderStudio_FastCorrected_LoRA_v1_0
   ```

8. Leave the optional expensive research controls and EC2 merge control
   `False` for the first clean pass. They can be run later from their individual
   cells without repeating training.
9. Run the remaining cells in displayed order.

The first notebook must produce:

```text
outputs/adapters/RepoCoderStudio_FastCorrected_LoRA_v1_0/
outputs/approved_corpus/approved_corpus.jsonl
outputs/corpus_index/corpus_index_manifest.json
outputs/repositories/ledgerflow/
outputs/evaluation/
outputs/reports/
```

Docker verification can correctly display `NOT_FEASIBLE` in Colab. Generation
is independent of Docker and is still saved. Do not treat `NOT_FEASIBLE` as a
model-generation failure.

## Step 2 — Run the final RAG-aware notebook

1. Open `notebooks/RepoCoderStudio_RAG_Augmented_Retrain.ipynb`.
2. Keep the same Drive folder and use a T4 GPU.
3. In a fresh runtime, run Step 1a once. It installs dependencies and restarts
   the kernel automatically. After reconnection, continue at Step 1b; do not
   rerun Step 1a.
4. Step 1b hard-fails if the first notebook's corpus or indexes are missing.
   Resolve the named missing path instead of bypassing the assertion.
5. Run Steps 2–9 in order. The notebook builds grounded RAG-formatted training
   rows, performs response-safe token budgeting and trains the separate v1.2
   adapter.
6. If the packaged or previously completed v1.2 adapter and manifest match, the
   training cell safely reuses them. It does not retrain merely because the
   notebook is being reopened.
7. Confirm these final messages:

   ```text
   Email benchmark success: True
   Exact policy constants/countries preserved: True
   Overall verification success: True
   ```

The final serving artifacts are:

```text
outputs/adapters/RepoCoderStudio_RAGAware_LoRA_v1_2/
outputs/reports/rag_grounded_retrain_v1_2_verification.json
outputs/task_datasets/task_dataset_rag_grounded.jsonl
```

# Part D — Reopen the Gradio demonstration without retraining

1. Start the RAG-aware notebook with a T4 GPU.
2. In a fresh session, run Step 1a, allow the restart, and continue at Step 1b.
3. Run the remaining cells in order. Existing matching artifacts cause the
   training cell to print that it is safely reusing the adapter.
4. The last cell starts Gradio. Open only the newly printed `gradio.live` URL;
   old share links expire and cannot be reused.
5. Keep the cell running while demonstrating the UI. The queue intentionally
   allows one generation at a time.

For the flagship comparison select:

```text
Repository context: LedgerFlow banking sample
Task contract     : T1 Natural Language → Python
Preloaded example : Implement transfer-risk policy
Models            : Baseline and Fine-tuned
Evidence modes    : No RAG and With RAG
```

The fine-tuned/with-RAG arm should recover the repository's exact thresholds,
weights, high-risk countries and `min(score, 100.0)` cap. Structural `PASS`
means valid syntax; the saved semantic checks support the stronger correctness
claim.

# Part E — Local FastAPI/Docker deployment

Docker Desktop or Docker Engine must be installed and running. From the project
root, create the local environment file:

Linux/macOS/Cloud Shell:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Build and launch:

```bash
docker compose up --build
```

Open `http://localhost:8000`, then
`http://localhost:8000/api/health`. The health response must name
`RepoCoderStudio_RAGAware_LoRA_v1_2`, report `mock_embeddings: false`, and show
the repository/corpus indexes as loaded. The first start downloads the base,
embedding and reranker models and therefore takes longer than later starts.

Stop the service with `Ctrl+C`, then:

```bash
docker compose down
```

# Part F — Deploy the FastAPI browser application to GCP Cloud Run

This section assumes **zero prior GCP experience** and a weak/slow local
computer, so the path below deliberately keeps almost everything in the
cloud: no local install, no local build. Your computer's only job is one
small (~97 MB) file upload in F.3; every other step — including the actual
Docker build — runs on Google's servers. A hardened/advanced path (separate
build step, safe zero-downtime redeploys, explicit IAM, secrets) follows
afterward for later — skip it for a first deploy.

## F.0 — Concepts, in plain terms

- **GCP project**: a container that holds your resources and billing, like a
  folder for this one app. You need exactly one. It has a human-readable
  name and a separate, permanent **Project ID** (e.g. `repocoder-471203`) —
  commands need the Project ID, not the name.
- **Billing account**: Cloud Run has an always-free monthly quota, but GCP
  still requires a billing account (a card on file) linked to the project
  before any API will work, even if you stay inside the free tier.
- **`gcloud`**: the command-line tool that talks to GCP. You will not
  install this on your computer — see Cloud Shell below.
- **Cloud Shell**: a free terminal that runs entirely in your browser,
  backed by a small temporary cloud VM with `gcloud` already installed and
  already signed in. This is where every command in this guide runs.
- **Artifact Registry**: GCP's storage for your built Docker image. You
  don't need to think about it — the command below creates and fills it
  automatically.
- **Cloud Build**: the service that builds your Docker image *inside GCP*,
  so neither your laptop nor Cloud Shell does the actual heavy lifting.
- **Cloud Run**: runs your container and gives you a public `https://...`
  URL. It scales to zero (no cost) when nobody is using it.

## F.1 — One-time account setup (browser)

1. Go to <https://console.cloud.google.com/projectcreate>, sign in, and
   create a project. Write down the **Project ID** shown under the project
   name — you'll paste it into a command below.
2. If prompted, link a billing account (Billing → link a billing account).
   New accounts get free trial credit; this project's Cloud Run usage during
   review/demo is expected to stay inside the free tier if you follow
   Step F.6's teardown command afterward.

## F.2 — Open Cloud Shell (no install, nothing runs on your computer)

Because your local machine is weak, skip installing anything at all. GCP
gives every project a free **Cloud Shell**: a terminal that opens right in
your browser, backed by a small cloud VM with `gcloud` already installed and
already signed in as you. From here on, every command in this guide runs
*there*, not on your computer — your computer only does one small file
upload (Step F.3) and then just displays a browser tab.

1. Go to <https://console.cloud.google.com>, make sure the project you
   created in F.1 is selected (top toolbar dropdown).
2. Click the **Activate Cloud Shell** icon (`>_`) near the top-right corner.
   A terminal panel opens at the bottom of the browser within a few seconds.
3. `gcloud` in that terminal is already authenticated and already pointed at
   your project — no `gcloud init`, no login prompt, nothing to install.

## F.3 — Get the deployment files into Cloud Shell (~97 MB, one upload)

Cloud Run only needs a small slice of this project to build the image: the
app code, plus the already-trained v1.2 adapter and the pre-built repository
and corpus indexes it serves at query time (not the raw training datasets or
notebooks). Package just that slice locally — this step is light file I/O,
not computation, so it's fine even on a weak machine.

From PowerShell, in the folder that contains `RepoCoderStudio/`:

```powershell
cd RepoCoderStudio
tar -a -c -f repocoder_deploy.zip `
  Dockerfile requirements.txt pyproject.toml `
  src app scripts repo_explorer_data `
  outputs/adapters/RepoCoderStudio_RAGAware_LoRA_v1_2 `
  outputs/approved_corpus `
  outputs/corpus_index `
  outputs/repositories
```

`outputs/corpus_index` and `outputs/repositories` are the retrieval side of
this app — the FAISS/embedding indexes and the parsed repository snapshots
(including LedgerFlow and the AWS SDK demo) that retrieval queries against at
serving time. Without them the container still starts, but repository-aware
retrieval has nothing to search. They're included above.

Now upload `repocoder_deploy.zip` into Cloud Shell:

1. In the Cloud Shell panel, click the **⋮** (three-dot) menu → **Upload**.
2. Choose `repocoder_deploy.zip` from your computer. It lands in Cloud
   Shell's home directory (`~`).
3. Back in the Cloud Shell terminal, unpack it:

```bash
mkdir -p RepoCoderStudio && cd RepoCoderStudio
unzip -q ~/repocoder_deploy.zip
```

Everything from here runs inside Cloud Shell, not your computer.

## F.4 — Deploy with one command

```bash
PROJECT_ID="replace-with-your-gcp-project-id"
REGION="asia-south1"

gcloud config set project "${PROJECT_ID}"

gcloud run deploy repocoder-studio \
  --source . \
  --region="${REGION}" \
  --allow-unauthenticated \
  --execution-environment=gen2 \
  --cpu=2 \
  --memory=8Gi \
  --concurrency=1 \
  --timeout=900 \
  --max-instances=1 \
  --min-instances=0 \
  --cpu-boost \
  --set-env-vars="REPOCODER_PROFILE=production,REPOCODER_ADAPTER_NAME=RepoCoderStudio_RAGAware_LoRA_v1_2,REPOCODER_PROMPT_VERSION=rag_prompt_contract_v1.2,REPOCODER_TRAINING_MANIFEST_VERSION=training_manifest_rag_v1.2,REPOCODER_TRAINING_DATASET_FILENAME=task_dataset_rag_grounded.jsonl,REPOCODER_MAX_CONTEXT_CHARS=2000,REPOCODER_ENABLE_RAG=true,REPOCODER_ALLOW_MOCK_EMBEDDINGS=false,REPOCODER_MAX_CONCURRENT_GENERATIONS=1"
```

`--source .` does everything in one step, entirely on Google's servers: it
builds the Docker image with Cloud Build, creates an Artifact Registry
repository automatically the first time, pushes the image, and deploys it to
Cloud Run. The first time you run it, `gcloud` will print prompts like *"API
[artifactregistry.googleapis.com] not enabled. Would you like to enable
it?"* and *"Create repository...?"* — answer `y` to each; this only happens
once per project.

`--execution-environment=gen2` and the resource flags match this project's
CPU inference profile (no GPU on Cloud Run): 2 vCPUs, 8 GiB memory, one
request at a time, and a 15-minute timeout because generation on CPU is slow.
`--allow-unauthenticated` makes the URL public, which is what you want for a
reviewer/demo link.

The command takes a few minutes (building, then deploying) and prints a
service URL like `https://repocoder-studio-xxxxx-el.a.run.app` when done. If
Cloud Shell disconnects from inactivity, reopen it (`⋮` → Reconnect) — the
unpacked `RepoCoderStudio/` folder in `~` persists across sessions, so you
don't need to re-upload the zip.

## F.5 — Check it worked, then note the URL

```bash
SERVICE_URL="$(gcloud run services describe repocoder-studio --region="${REGION}" --format='value(status.url)')"
echo "${SERVICE_URL}"
curl --fail --show-error --max-time 120 "${SERVICE_URL}/api/health"
```

Open `${SERVICE_URL}` in a browser — from any device, this URL is public and
does not involve Cloud Shell or your computer at all once deployed.
`/api/health` should name `RepoCoderStudio_RAGAware_LoRA_v1_2` and report
loaded indexes (see `START_HERE.md`). If the container is still starting,
the first request can take a minute or two — that's expected on a cold
start.

## F.6 — Turn it off when you're done (avoid ongoing cost)

`--min-instances=0` means Cloud Run already scales to zero and costs nothing
while idle, but delete the service when you're fully done reviewing so it
stops appearing at all. Run this in Cloud Shell (`~/RepoCoderStudio`):

```bash
gcloud run services delete repocoder-studio --region="${REGION}" --quiet
```

## F.7 — Redeploying after a code change

If you only changed code (not the adapter/indexes), re-zip just the changed
top-level items from F.3, upload the new zip into Cloud Shell, and overwrite:

```bash
unzip -q -o ~/repocoder_deploy.zip -d ~/RepoCoderStudio
```

Then rerun the same `gcloud run deploy --source . ...` command from F.4 from
inside `~/RepoCoderStudio`. It rebuilds and replaces the running version;
nothing else needs to be recreated. Cloud Shell's home directory persists
between sessions, so you don't need to redo F.2.

---

## Advanced / hardened path (optional, for later)

Everything below is optional polish on top of F.3 — a real capstone demo
does not need it. Use it once you're comfortable with the basics, e.g. before
sharing the URL widely, or if you want zero-downtime redeploys.

```bash
PROJECT_ID="replace-with-your-gcp-project-id"
REGION="asia-south1"
REPOSITORY="repocoder-images"
IMAGE="repocoder-studio"
SERVICE="repocoder-studio"
TAG="v1-2"
IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE}:${TAG}"

gcloud config set project "${PROJECT_ID}"
gcloud config set run/region "${REGION}"
gcloud services enable artifactregistry.googleapis.com cloudbuild.googleapis.com run.googleapis.com

gcloud artifacts repositories describe "${REPOSITORY}" --location "${REGION}" || \
gcloud artifacts repositories create "${REPOSITORY}" \
  --repository-format=docker --location="${REGION}" \
  --description="RepoCoder Studio container images"

gcloud builds submit --tag "${IMAGE_URI}" .
```

Deploy without sending traffic yet, so a bad build never reaches the public
URL:

```bash
gcloud run deploy "${SERVICE}" \
  --image="${IMAGE_URI}" --region="${REGION}" --platform=managed \
  --execution-environment=gen2 --no-traffic --tag="${TAG}" \
  --cpu=2 --memory=8Gi --concurrency=1 --timeout=900 \
  --max-instances=1 --min-instances=0 --cpu-boost \
  --set-env-vars="REPOCODER_PROFILE=production,REPOCODER_ADAPTER_NAME=RepoCoderStudio_RAGAware_LoRA_v1_2,REPOCODER_PROMPT_VERSION=rag_prompt_contract_v1.2,REPOCODER_TRAINING_MANIFEST_VERSION=training_manifest_rag_v1.2,REPOCODER_TRAINING_DATASET_FILENAME=task_dataset_rag_grounded.jsonl,REPOCODER_MAX_CONTEXT_CHARS=2000,REPOCODER_ENABLE_RAG=true,REPOCODER_ALLOW_MOCK_EMBEDDINGS=false,REPOCODER_MAX_CONCURRENT_GENERATIONS=1"
```

Smoke-test the untraffic'd revision on its own preview URL, then shift
traffic only once it's healthy:

```bash
PREVIEW_URL="$(gcloud run revisions list --service="${SERVICE}" --region="${REGION}" \
  --format='value(status.url)' --filter="metadata.labels.'run.googleapis.com/revision-tag'=${TAG}" | head -n1)"
curl --fail --show-error --max-time 120 "${PREVIEW_URL}/api/health"

gcloud run services update-traffic "${SERVICE}" --region="${REGION}" --to-latest
```

Grant public access as an explicit, auditable IAM step instead of relying on
`--allow-unauthenticated` (this also still works on projects where an org
policy silently blocks that flag during `deploy`):

```bash
gcloud run services add-iam-policy-binding "${SERVICE}" --region="${REGION}" \
  --member="allUsers" --role="roles/run.invoker"
```

For anything beyond a capstone demo, put `REPOCODER_API_KEY` in Secret
Manager instead of a plain `--set-env-vars` value:

```bash
PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
printf '%s' "replace-with-a-real-key" | gcloud secrets create repocoder-api-key --data-file=-
gcloud secrets add-iam-policy-binding repocoder-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
# then redeploy adding: --set-secrets="REPOCODER_API_KEY=repocoder-api-key:latest"
```

Clean up the built image along with the service when finished:

```bash
gcloud run services delete "${SERVICE}" --region="${REGION}" --quiet
gcloud artifacts docker images delete "${IMAGE_URI}" --delete-tags --quiet
```

To redeploy later without downtime: bump `TAG` (e.g. `v1-3`) and repeat the
build → `--no-traffic` deploy → smoke test → `update-traffic` sequence above.
If the smoke test fails, just fix the code and rerun — the previous good
revision keeps serving all traffic until `update-traffic` is run.

The following AWS EC2 steps are optional. They only replace Colab's
`NOT_FEASIBLE` Docker checks with isolated functional results and do not affect
training, Gradio, FastAPI or Cloud Run deployment.

The following AWS EC2 steps are optional. They only replace Colab's
`NOT_FEASIBLE` Docker checks with isolated functional results and do not affect
training, Gradio, FastAPI or Cloud Run deployment.

# Part G — Optional AWS EC2 functional verification

The original Step 6–9 numbering is retained below because the copyable
evaluator script refers to those exact step numbers.

# Step 6 — Launch AWS EC2 and install Docker

1. In AWS EC2, launch Amazon Linux 2023 on an eligible small instance.
2. Enable a public IPv4 address.
3. Create a new security group.
4. Allow SSH only from **My IP** where possible.
5. Leave HTTP and HTTPS unchecked.
6. In the root-volume advanced settings, keep **Delete on termination = Yes**.
7. Connect using **EC2 Instance Connect**.

Run:

```bash
sudo dnf update -y
sudo dnf install -y docker python3
sudo systemctl enable --now docker
sudo usermod -aG docker ec2-user
exit
```

Reconnect with EC2 Instance Connect, then run:

```bash
docker version
python3 --version
```

Both commands must succeed.

# Step 7 — Create the evaluator and four generated-code files

Create the script:

```bash
nano repocoder_docker_eval.py
```

Paste the complete script below, save with `Ctrl+O`, Enter, then exit with `Ctrl+X`.

```python
"""Standalone Docker functional-correctness evaluator for RepoCoder Studio.

Runs entirely on the standard library -- no torch/transformers/faiss, no
`src.*` package imports, no network access except pulling the two Docker
images the first time. Designed to run on a machine that has real generation
results (produced separately, e.g. in the Colab notebook) but no GPU and no
project checkout: only this one file, plus Docker, is required.

What it does
------------
1. Self-test: runs the curated cases against known-correct source (the
   project's own demo-repo functions, embedded below) to prove the Docker
   harness itself works, before trusting it to judge model output.
2. Verification: if `no_rag_python.txt` / `rag_python.txt` / `no_rag_java.txt`
   / `rag_java.txt` exist in the current directory, runs the same functional
   comparison the notebook's Cell 26D runs, using whatever code you pasted
   into those files.
3. Prints one JSON object to stdout (copy it back into Colab and use
   RUNBOOK.md Step 8 to merge its Docker-dependent sections into
   "outputs/reports/functional_eval_report.json" without replacing the
   Colab-generated evidence) and also saves it to
   `functional_eval_report.json` next to this script.

Usage
-----
    python3 repocoder_docker_eval.py

See RUNBOOK.md for the full step-by-step (EC2 setup, Docker install, how to
get the four *.txt files onto this machine).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

# ============================================================
# extract_code() -- verbatim copy of src/code_extraction.py
# ============================================================


def extract_code(prediction: str, language: str) -> str:
    text = prediction or ""
    fence = re.search(r"```(?:python|py|java)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    text = re.sub(r"^(Here is|Sure, here is|The code is|Below is).*?:", "", text, flags=re.I | re.S).strip()
    if language.lower() == "python":
        for marker in ["###", "```", "Explanation:", "Java:"]:
            if marker in text:
                text = text.split(marker, 1)[0].strip()
    if language.lower() == "java":
        for marker in ["###", "```", "Explanation:", "Python:"]:
            if marker in text:
                text = text.split(marker, 1)[0].strip()
    return text.strip()


# ============================================================
# Functional-eval harness -- verbatim copy of
# src/functional_execution_eval.py
# ============================================================


@dataclass(frozen=True)
class FunctionalCase:
    case_id: str
    function_name: str
    args: List[Any]
    kwargs: Dict[str, Any]
    expected: Any


@dataclass(frozen=True)
class JavaFunctionalCase:
    case_id: str
    class_name: str
    method_name: str
    arg_literals: List[str] = field(default_factory=list)
    expected_literal: str = "null"
    static: bool = False


@dataclass(frozen=True)
class FunctionalResult:
    case_id: str
    status: str
    passed: bool
    detail: str = ""


_RUNNER = r"""
import importlib.util
import json
import sys

spec = importlib.util.spec_from_file_location("candidate", "/work/candidate.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
cases = json.load(open("/work/cases.json", encoding="utf-8"))
results = []
for case in cases:
    try:
        fn = getattr(module, case["function_name"])
        actual = fn(*case.get("args", []), **case.get("kwargs", {}))
        passed = actual == case.get("expected")
        results.append({
            "case_id": case["case_id"],
            "status": "PASS" if passed else "FAIL",
            "passed": passed,
            "detail": "" if passed else f"expected={case.get('expected')!r}, actual={actual!r}",
        })
    except Exception as exc:
        results.append({
            "case_id": case["case_id"],
            "status": "ERROR",
            "passed": False,
            "detail": f"{type(exc).__name__}: {exc}",
        })
print(json.dumps(results))
"""


def _docker_available() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        completed = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],
            check=False, capture_output=True, text=True, timeout=5,
        )
        return completed.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _ensure_docker_image(image: str, timeout_seconds: int) -> Optional[str]:
    try:
        inspect = subprocess.run(
            ["docker", "image", "inspect", image],
            check=False, capture_output=True, text=True, timeout=10,
        )
        if inspect.returncode == 0:
            return None
        pull = subprocess.run(
            ["docker", "pull", image],
            check=False, capture_output=True, text=True, timeout=timeout_seconds,
        )
        if pull.returncode == 0:
            return None
        return (pull.stderr or pull.stdout or "Docker image pull failed")[-2000:]
    except subprocess.TimeoutExpired:
        return f"Docker image pull/inspect timed out after {timeout_seconds} seconds"
    except OSError as exc:
        return f"Docker image could not be prepared: {exc}"


def _isolation_flags(container_name: str, memory: str, cpus: str, tmpfs_size: str) -> List[str]:
    return [
        "--name", container_name,
        "--network", "none",
        "--read-only",
        "--user", "65534:65534",
        "--memory", memory,
        "--cpus", cpus,
        "--pids-limit", "64",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--tmpfs", f"/tmp:rw,noexec,nosuid,size={tmpfs_size}",
    ]


def _kill_container(name: str) -> None:
    try:
        subprocess.run(["docker", "kill", name], check=False, capture_output=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        pass


def _run_docker(command: List[str], timeout_seconds: int, container_name: str):
    try:
        completed = subprocess.run(
            command, check=False, capture_output=True, text=True, timeout=timeout_seconds,
        )
        return completed, None
    except subprocess.TimeoutExpired:
        _kill_container(container_name)
        return None, _summary([], "TIMEOUT", "container execution timed out")
    except OSError as exc:
        return None, _summary([], "NOT_FEASIBLE", f"Docker could not start: {exc}")


def _summary(results: List[FunctionalResult], status: str, reason: str) -> Dict[str, Any]:
    passed = sum(result.passed for result in results)
    return {
        "status": status,
        "reason": reason,
        "cases": [asdict(result) for result in results],
        "cases_run": len(results),
        "cases_passed": passed,
        "pass_rate": passed / len(results) if results else None,
        "execution_isolated": status != "NOT_FEASIBLE",
        "isolation": "docker:no-network,read-only,resource-limited",
    }


class DockerPythonEvaluator:
    def __init__(self, image="python:3.11-slim", timeout_seconds=15, memory="256m", cpus="0.5", image_pull_timeout_seconds=300):
        self.image = image
        self.timeout_seconds = timeout_seconds
        self.image_pull_timeout_seconds = image_pull_timeout_seconds
        self.memory = memory
        self.cpus = cpus

    @staticmethod
    def available() -> bool:
        return _docker_available()

    def evaluate(self, code: str, cases: Iterable[FunctionalCase]) -> Dict[str, Any]:
        cases = list(cases)
        if not cases:
            return _summary([], "NOT_FEASIBLE", "no trusted functional cases")
        if not self.available():
            return _summary([], "NOT_FEASIBLE", "Docker is unavailable; code was not executed")
        image_error = _ensure_docker_image(self.image, self.image_pull_timeout_seconds)
        if image_error is not None:
            return _summary([], "NOT_FEASIBLE", image_error)

        with tempfile.TemporaryDirectory(prefix="repocoder_functional_") as temp:
            root = Path(temp)
            candidate_path = root / "candidate.py"
            runner_path = root / "runner.py"
            cases_path = root / "cases.json"
            candidate_path.write_text(code or "", encoding="utf-8")
            runner_path.write_text(_RUNNER, encoding="utf-8")
            cases_path.write_text(json.dumps([asdict(c) for c in cases]), encoding="utf-8")
            # TemporaryDirectory is 0700 on Linux. The evaluator container
            # deliberately runs as UID/GID 65534, so make only this ephemeral
            # read-only bind-mount tree traversable/readable by that user.
            root.chmod(0o755)
            for path in (candidate_path, runner_path, cases_path):
                path.chmod(0o644)
            container_name = f"repocoder-func-eval-{uuid.uuid4().hex[:12]}"
            command = [
                "docker", "run", "--rm",
                *_isolation_flags(container_name, self.memory, self.cpus, "16m"),
                "-v", f"{root.resolve()}:/work:ro",
                self.image, "python", "-I", "/work/runner.py",
            ]
            completed, error = _run_docker(command, self.timeout_seconds, container_name)
            if error is not None:
                return error
            if completed.returncode != 0:
                detail = (completed.stderr or completed.stdout or "container failed")[-2000:]
                return _summary([], "ERROR", detail)
            try:
                rows = json.loads(completed.stdout.strip().splitlines()[-1])
                results = [FunctionalResult(**row) for row in rows]
            except (json.JSONDecodeError, IndexError, TypeError, ValueError) as exc:
                return _summary([], "ERROR", f"invalid runner output: {exc}")
            return _summary(results, "COMPLETE", "")


_JAVA_IDENTIFIER = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")
_JAVA_PACKAGE = re.compile(r"(?m)^\s*package\s+([A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*)\s*;")


def _java_package_name(code: str) -> str:
    match = _JAVA_PACKAGE.search(code or "")
    return match.group(1) if match else ""


def _java_runner_source(cases: List[JavaFunctionalCase], package_name: str = "") -> str:
    blocks = []
    for index, case in enumerate(cases):
        if not _JAVA_IDENTIFIER.fullmatch(case.class_name):
            raise ValueError(f"invalid Java class name in functional case: {case.class_name!r}")
        if not _JAVA_IDENTIFIER.fullmatch(case.method_name):
            raise ValueError(f"invalid Java method name in functional case: {case.method_name!r}")
        args_src = ", ".join(case.arg_literals)
        call = (
            f"{case.class_name}.{case.method_name}({args_src})"
            if case.static
            else f"new {case.class_name}().{case.method_name}({args_src})"
        )
        case_id = case.case_id.replace("\\", "\\\\").replace('"', '\\"')
        blocks.append(
            f"""
        try {{
            Object result{index} = {call};
            Object expected{index} = {case.expected_literal};
            boolean passed{index} = java.util.Objects.equals(result{index}, expected{index});
            out.append("{case_id}|" + (passed{index} ? "PASS" : "FAIL") + "|" +
                (passed{index} ? "" : ("expected=" + expected{index} + " actual=" + result{index})) + "\\n");
        }} catch (Throwable t{index}) {{
            out.append("{case_id}|ERROR|" + t{index}.getClass().getSimpleName() + ": " + t{index}.getMessage() + "\\n");
        }}"""
        )
    body = "\n".join(blocks)
    package_line = f"package {package_name};\n\n" if package_name else ""
    return f"""{package_line}public class Runner {{
    public static void main(String[] args) {{
        StringBuilder out = new StringBuilder();
{body}
        System.out.print(out);
    }}
}}
"""


class DockerJavaEvaluator:
    def __init__(self, image="eclipse-temurin:17-jdk-alpine", timeout_seconds=20, memory="384m", cpus="0.5", image_pull_timeout_seconds=300):
        self.image = image
        self.timeout_seconds = timeout_seconds
        self.image_pull_timeout_seconds = image_pull_timeout_seconds
        self.memory = memory
        self.cpus = cpus

    @staticmethod
    def available() -> bool:
        return _docker_available()

    def evaluate(self, code: str, class_name: str, cases: Iterable[JavaFunctionalCase]) -> Dict[str, Any]:
        cases = list(cases)
        if not cases:
            return _summary([], "NOT_FEASIBLE", "no trusted functional cases")
        if not self.available():
            return _summary([], "NOT_FEASIBLE", "Docker is unavailable; code was not executed")
        image_error = _ensure_docker_image(self.image, self.image_pull_timeout_seconds)
        if image_error is not None:
            return _summary([], "NOT_FEASIBLE", image_error)
        if not _JAVA_IDENTIFIER.fullmatch(class_name or ""):
            return _summary([], "ERROR", f"invalid Java class name: {class_name!r}")

        package_name = _java_package_name(code)
        runner_class = f"{package_name}.Runner" if package_name else "Runner"

        with tempfile.TemporaryDirectory(prefix="repocoder_functional_java_") as temp:
            root = Path(temp)
            candidate_path = root / f"{class_name}.java"
            candidate_path.write_text(code or "", encoding="utf-8")
            try:
                runner_source = _java_runner_source(cases, package_name=package_name)
            except ValueError as exc:
                return _summary([], "ERROR", str(exc))
            runner_path = root / "Runner.java"
            runner_path.write_text(runner_source, encoding="utf-8")
            # See DockerPythonEvaluator: the non-root container must be able
            # to traverse the host temporary directory and read both sources.
            root.chmod(0o755)
            for path in (candidate_path, runner_path):
                path.chmod(0o644)
            container_name = f"repocoder-func-eval-java-{uuid.uuid4().hex[:12]}"
            command = [
                "docker", "run", "--rm",
                *_isolation_flags(container_name, self.memory, self.cpus, "48m"),
                "-e", "HOME=/tmp",
                "-v", f"{root.resolve()}:/work:ro",
                self.image, "sh", "-c",
                f"javac -d /tmp /work/*.java && java -cp /tmp {runner_class}",
            ]
            completed, error = _run_docker(command, self.timeout_seconds, container_name)
            if error is not None:
                return error
            if completed.returncode != 0:
                detail = (completed.stderr or completed.stdout or "container failed")[-2000:]
                return _summary([], "ERROR", detail)
            try:
                results = []
                for line in completed.stdout.splitlines():
                    if not line.strip():
                        continue
                    case_id, status, detail = line.split("|", 2)
                    results.append(FunctionalResult(case_id=case_id, status=status, passed=(status == "PASS"), detail=detail))
                if len(results) != len(cases):
                    return _summary(results, "ERROR", f"expected {len(cases)} result lines, got {len(results)}")
            except ValueError as exc:
                return _summary([], "ERROR", f"invalid runner output: {exc}")
            return _summary(results, "COMPLETE", "")


def compare_functional_outputs(no_rag_code, rag_code, cases, evaluator=None) -> Dict[str, Any]:
    evaluator = evaluator or DockerPythonEvaluator()
    cases = list(cases)
    no_rag = evaluator.evaluate(extract_code(no_rag_code, "python"), cases)
    with_rag = evaluator.evaluate(extract_code(rag_code, "python"), cases)
    return {"no_rag": no_rag, "with_rag": with_rag, "pass_rate_lift": _pass_rate_lift(no_rag, with_rag)}


def compare_java_functional_outputs(no_rag_code, rag_code, class_name, cases, evaluator=None) -> Dict[str, Any]:
    evaluator = evaluator or DockerJavaEvaluator()
    cases = list(cases)
    no_rag = evaluator.evaluate(extract_code(no_rag_code, "java"), class_name, cases)
    with_rag = evaluator.evaluate(extract_code(rag_code, "java"), class_name, cases)
    return {"no_rag": no_rag, "with_rag": with_rag, "pass_rate_lift": _pass_rate_lift(no_rag, with_rag)}


def _pass_rate_lift(no_rag, with_rag) -> Optional[float]:
    no_rate = no_rag.get("pass_rate")
    rag_rate = with_rag.get("pass_rate")
    if isinstance(no_rate, (int, float)) and isinstance(rag_rate, (int, float)):
        return rag_rate - no_rate
    return None


# ============================================================
# Self-test fixtures -- same cases and known-correct source as
# notebook Cell 26D, so results here are directly comparable to
# whatever Colab could not execute.
# ============================================================

PYTHON_CASES = [
    FunctionalCase("flag_below_threshold", "flag_suspicious_transaction", [69.9], {"threshold": 70.0}, False),
    FunctionalCase("flag_at_threshold", "flag_suspicious_transaction", [70.0], {"threshold": 70.0}, True),
    FunctionalCase("risk_score_moderate", "calculate_risk_score", [50000, 10000, False], {}, 50.0),
    FunctionalCase("risk_score_capped", "calculate_risk_score", [150000, 10000, True], {}, 100.0),
    FunctionalCase("round_amounts_flagged", "detect_round_amount_pattern", [[1000.0, 2000.0, 3000.0, 1500.0]], {}, True),
    FunctionalCase("round_amounts_clear", "detect_round_amount_pattern", [[1500.0, 2500.0]], {}, False),
    FunctionalCase("pan_valid", "validate_pan", ["ABCDE1234F"], {}, True),
    FunctionalCase("pan_invalid", "validate_pan", ["invalid"], {}, False),
    FunctionalCase("aadhaar_valid", "validate_aadhaar", ["123456789012"], {}, True),
    FunctionalCase("mask_pan_example", "mask_pan", ["abcde1234f"], {}, "******234F"),
    FunctionalCase("transfer_low_risk", "transfer_risk_score", [50000, 365, "US", True], {}, 0.0),
    FunctionalCase("transfer_amount_boundary", "transfer_risk_score", [100000, 365, "US", True], {}, 25.0),
    FunctionalCase("transfer_combined_risk", "transfer_risk_score", [120000, 10, "IR", False], {}, 90.0),
    FunctionalCase("transfer_risk_capped", "transfer_risk_score", [300000, 10, "SY", False], {}, 100.0),
]

FRAUD_DETECTOR_JAVA_CASES = [
    JavaFunctionalCase("flag_below_threshold", "FraudDetector", "flagSuspiciousTransaction", ["69.9", "70.0"], "false"),
    JavaFunctionalCase("flag_at_threshold", "FraudDetector", "flagSuspiciousTransaction", ["70.0", "70.0"], "true"),
    JavaFunctionalCase("risk_score_capped", "FraudDetector", "calculateRiskScore", ["150000", "10000", "true"], "100.0"),
]
KYC_VALIDATOR_JAVA_CASES = [
    JavaFunctionalCase("pan_valid", "KycValidator", "validatePan", ['"ABCDE1234F"'], "true"),
    JavaFunctionalCase("mask_pan_example", "KycValidator", "maskPan", ['"abcde1234f"'], '"******234F"'),
]
TRANSFER_POLICY_JAVA_CASES = [
    JavaFunctionalCase("transfer_low_risk", "TransferPolicy", "transferRiskScore", ["50000", "365", '"US"', "true"], "0.0"),
    JavaFunctionalCase("transfer_amount_boundary", "TransferPolicy", "transferRiskScore", ["100000", "365", '"US"', "true"], "25.0"),
    JavaFunctionalCase("transfer_combined_risk", "TransferPolicy", "transferRiskScore", ["120000", "10", '"IR"', "false"], "90.0"),
    JavaFunctionalCase("transfer_risk_capped", "TransferPolicy", "transferRiskScore", ["300000", "10", '"SY"', "false"], "100.0"),
]

PYTHON_SELF_TEST_SOURCE = '''
import re


def flag_suspicious_transaction(risk_score, threshold=70.0):
    return risk_score >= threshold


def calculate_risk_score(amount, account_avg_transaction, is_new_payee):
    score = 0.0
    if account_avg_transaction > 0:
        ratio = amount / account_avg_transaction
        score += min(ratio * 10, 60)
    if is_new_payee:
        score += 25
    if amount > 100_000:
        score += 15
    return min(score, 100.0)


def detect_round_amount_pattern(amounts):
    round_count = sum(1 for a in amounts if a % 1000 == 0 and a > 0)
    return len(amounts) > 0 and (round_count / len(amounts)) > 0.6


def validate_pan(pan_number):
    return bool(re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]{1}", pan_number.strip().upper()))


def validate_aadhaar(aadhaar_number):
    digits = aadhaar_number.replace(" ", "")
    return digits.isdigit() and len(digits) == 12


def mask_pan(pan_number):
    pan_number = pan_number.strip().upper()
    if len(pan_number) < 4:
        return "*" * len(pan_number)
    return "*" * (len(pan_number) - 4) + pan_number[-4:]


def transfer_risk_score(amount, customer_tenure_days, destination_country, trusted_device):
    high_risk_countries = {"IR", "KP", "SY"}
    score = 0.0
    if amount >= 250_000:
        score += 40
    elif amount >= 100_000:
        score += 25
    if customer_tenure_days < 30:
        score += 20
    if destination_country.strip().upper() in high_risk_countries:
        score += 30
    if not trusted_device:
        score += 15
    return min(score, 100.0)
'''

# Verbatim copies of repo_explorer_data/sample_repo/transactions/FraudDetector.java
# and .../accounts/KycValidator.java -- the two already-migrated demo classes.
FRAUD_DETECTOR_JAVA_SOURCE = '''package transactions;

import java.util.List;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

/**
 * Fraud detection heuristics for the demo BFSI sample repository.
 *
 * Java counterpart of transactions/fraud_detector.py -- same heuristics,
 * kept in step with the Python version so Stage 4/5 has a genuinely
 * bilingual repository to index rather than a Python-only demo.
 */
public class FraudDetector {

    /**
     * Compute a 0-100 fraud risk score for a transaction based on amount
     * and payee history.
     */
    public double calculateRiskScore(double amount, double accountAvgTransaction, boolean isNewPayee) {
        double score = 0.0;
        if (accountAvgTransaction > 0) {
            double ratio = amount / accountAvgTransaction;
            score += Math.min(ratio * 10, 60);
        }
        if (isNewPayee) {
            score += 25;
        }
        if (amount > 100000) {
            score += 15;
        }
        return Math.min(score, 100.0);
    }

    /**
     * Decide whether a transaction should be flagged for manual fraud
     * review.
     */
    public boolean flagSuspiciousTransaction(double riskScore, double threshold) {
        return riskScore >= threshold;
    }

    /**
     * Return true if too many transactions have occurred within a short
     * time window (velocity fraud check).
     */
    public boolean checkVelocityLimit(List<LocalDateTime> recentTransactionTimes, int windowMinutes, int maxCount) {
        if (recentTransactionTimes.isEmpty()) {
            return false;
        }
        LocalDateTime cutoff = LocalDateTime.now().minus(windowMinutes, ChronoUnit.MINUTES);
        int recentCount = 0;
        for (LocalDateTime t : recentTransactionTimes) {
            if (!t.isBefore(cutoff)) {
                recentCount++;
            }
        }
        return recentCount > maxCount;
    }

    /**
     * Flag a suspicious pattern of suspiciously round transaction
     * amounts, often seen in structuring/smurfing.
     */
    public boolean detectRoundAmountPattern(List<Double> amounts) {
        if (amounts.isEmpty()) {
            return false;
        }
        long roundCount = 0;
        for (double a : amounts) {
            if (a > 0 && a % 1000 == 0) {
                roundCount++;
            }
        }
        return ((double) roundCount / amounts.size()) > 0.6;
    }
}
'''

KYC_VALIDATOR_JAVA_SOURCE = '''package accounts;

import java.util.HashMap;
import java.util.Map;

/**
 * Customer identity verification (KYC) for the demo BFSI sample repository.
 *
 * Java counterpart of accounts/kyc_validator.py -- same checks, kept in
 * step with the Python version so Stage 4/5 has a genuinely bilingual
 * repository to index rather than a Python-only demo.
 */
public class KycValidator {

    /**
     * Check whether a string matches the Indian PAN card format (5
     * letters, 4 digits, 1 letter).
     */
    public boolean validatePan(String panNumber) {
        String normalized = panNumber.trim().toUpperCase();
        return normalized.matches("[A-Z]{5}[0-9]{4}[A-Z]{1}");
    }

    /**
     * Check whether a string is a plausible 12-digit Aadhaar number.
     */
    public boolean validateAadhaar(String aadhaarNumber) {
        String digits = aadhaarNumber.replace(" ", "");
        return digits.matches("[0-9]+") && digits.length() == 12;
    }

    /**
     * Run full KYC identity verification, combining PAN and Aadhaar
     * checks.
     */
    public Map<String, Boolean> verifyIdentity(String panNumber, String aadhaarNumber, String fullName) {
        boolean panOk = validatePan(panNumber);
        boolean aadhaarOk = validateAadhaar(aadhaarNumber);
        boolean nameOk = fullName != null && !fullName.trim().isEmpty();

        Map<String, Boolean> result = new HashMap<>();
        result.put("verified", panOk && aadhaarOk && nameOk);
        result.put("panValid", panOk);
        result.put("aadhaarValid", aadhaarOk);
        result.put("nameProvided", nameOk);
        return result;
    }

    /**
     * Mask a PAN number for display, keeping only the last 4 characters
     * visible.
     */
    public String maskPan(String panNumber) {
        String normalized = panNumber.trim().toUpperCase();
        if (normalized.length() < 4) {
            return "*".repeat(normalized.length());
        }
        String visible = normalized.substring(normalized.length() - 4);
        return "*".repeat(normalized.length() - 4) + visible;
    }
}
'''

TRANSFER_POLICY_JAVA_SOURCE = '''package policies;

import java.util.Map;
import java.util.Set;

public class TransferPolicy {
    public double transferRiskScore(
        double amount, int customerTenureDays, String destinationCountry, boolean trustedDevice
    ) {
        Set<String> highRiskCountries = Set.of("IR", "KP", "SY");
        double score = 0.0;
        if (amount >= 250000) {
            score += 40;
        } else if (amount >= 100000) {
            score += 25;
        }
        if (customerTenureDays < 30) {
            score += 20;
        }
        if (highRiskCountries.contains(destinationCountry.trim().toUpperCase())) {
            score += 30;
        }
        if (!trustedDevice) {
            score += 15;
        }
        return Math.min(score, 100.0);
    }

    public boolean requiresStepUpAuth(double riskScore) {
        return riskScore >= 50.0;
    }

}
'''


def _not_feasible_pair(reason: str) -> Dict[str, Any]:
    result = {
        "status": "NOT_FEASIBLE", "reason": reason, "cases": [], "cases_run": 0,
        "cases_passed": 0, "pass_rate": None, "execution_isolated": False,
        "isolation": "docker:no-network,read-only,resource-limited",
    }
    return {"no_rag": dict(result), "with_rag": dict(result), "pass_rate_lift": None}


def _read_if_present(path: Path) -> Optional[str]:
    return path.read_text(encoding="utf-8") if path.exists() else None


def main() -> None:
    here = Path(__file__).resolve().parent
    docker_available = DockerPythonEvaluator.available()
    print(f"Docker daemon available: {docker_available}")

    python_evaluator = DockerPythonEvaluator()
    java_evaluator = DockerJavaEvaluator()

    print("\n--- Self-test (known-correct source) ---")
    python_self_test = python_evaluator.evaluate(PYTHON_SELF_TEST_SOURCE, PYTHON_CASES)
    print(f"Python: {python_self_test['status']} ({python_self_test['cases_passed']}/{python_self_test['cases_run']} passed)")

    java_self_test_results = {}
    if docker_available:
        java_self_test_results["FraudDetector"] = java_evaluator.evaluate(
            FRAUD_DETECTOR_JAVA_SOURCE, "FraudDetector", FRAUD_DETECTOR_JAVA_CASES
        )
        java_self_test_results["KycValidator"] = java_evaluator.evaluate(
            KYC_VALIDATOR_JAVA_SOURCE, "KycValidator", KYC_VALIDATOR_JAVA_CASES
        )
        java_self_test_results["TransferPolicy"] = java_evaluator.evaluate(
            TRANSFER_POLICY_JAVA_SOURCE, "TransferPolicy", TRANSFER_POLICY_JAVA_CASES
        )
    else:
        for class_name in ("FraudDetector", "KycValidator", "TransferPolicy"):
            java_self_test_results[class_name] = _not_feasible_pair(
                "Docker is unavailable; code was not executed"
            )["no_rag"]
    for class_name, result in java_self_test_results.items():
        print(f"Java ({class_name}): {result['status']} ({result['cases_passed']}/{result['cases_run']} passed)")

    print("\n--- Verification (generated code from Colab, if present) ---")
    no_rag_python = _read_if_present(here / "no_rag_python.txt")
    rag_python = _read_if_present(here / "rag_python.txt")
    no_rag_java = _read_if_present(here / "no_rag_java.txt")
    rag_java = _read_if_present(here / "rag_java.txt")

    python_harness_ready = python_self_test["status"] == "COMPLETE" and python_self_test["cases_passed"] == len(PYTHON_CASES)
    java_harness_ready = all(
        r["status"] == "COMPLETE" and r["cases_passed"] == r["cases_run"] and r["cases_run"] > 0
        for r in java_self_test_results.values()
    )

    if no_rag_python is not None and rag_python is not None:
        if python_harness_ready:
            python_verification = compare_functional_outputs(
                no_rag_python, rag_python, PYTHON_CASES[10:14], evaluator=python_evaluator
            )
        else:
            python_verification = _not_feasible_pair("Python Docker harness self-test did not pass.")
    else:
        python_verification = _not_feasible_pair(
            "no_rag_python.txt / rag_python.txt not found next to this script -- see RUNBOOK.md Step 6e."
        )

    if no_rag_java is not None and rag_java is not None:
        if java_harness_ready:
            java_verification = compare_java_functional_outputs(
                no_rag_java,
                rag_java,
                "TransferPolicy",
                TRANSFER_POLICY_JAVA_CASES,
                evaluator=java_evaluator,
            )
        else:
            java_verification = _not_feasible_pair("Java Docker harness self-test did not pass.")
    else:
        java_verification = _not_feasible_pair(
            "no_rag_java.txt / rag_java.txt not found next to this script -- see RUNBOOK.md Step 6e."
        )

    for language, comparison in (("python", python_verification), ("java", java_verification)):
        print(f"\n{language.title()} verification:")
        for mode in ("no_rag", "with_rag"):
            r = comparison[mode]
            print(f"  {mode}: {r['status']} ({r['cases_passed']}/{r['cases_run']} passed)")
            if r["status"] == "NOT_FEASIBLE":
                print(f"    Reason: {r['reason']}")
        print(f"  pass_rate_lift: {comparison['pass_rate_lift']}")

    report = {
        "python_self_test": python_self_test,
        "java_self_test": java_self_test_results,
        "verification": {"python": python_verification, "java": java_verification},
    }
    out_path = here / "functional_eval_report.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print("JSON result (copy everything below back into Colab):")
    print("=" * 60)
    print(json.dumps(report))
    print(f"\nAlso saved locally to {out_path}")


if __name__ == "__main__":
    main()
```

Create each generated-code file:

```bash
nano no_rag_python.txt
nano rag_python.txt
nano no_rag_java.txt
nano rag_java.txt
```

Paste the matching code copied in Step 5e into each file.

Run:

```bash
python3 repocoder_docker_eval.py
```

Expected harness self-tests:

- Python: 14/14;
- Java `FraudDetector`: 3/3;
- Java `KycValidator`: 2/2;
- Java `TransferPolicy`: 4/4.

The generated-code comparison then runs four repository-policy cases for Python and four for Java. Copy the one-line JSON printed after:

```text
JSON result (copy everything below back into Colab):
```

# Step 8 — Merge the EC2 result in Colab

Return to Colab and open the merge cell immediately after the extraction cell.

Replace only:

```text
PASTE_EC2_JSON_HERE
```

with the one-line EC2 JSON. Preserve the raw triple-quoted string and run the cell.

The merge cell preserves the Colab generation evidence and replaces only Docker-dependent sections.

Inspect:

```text
outputs/reports/functional_eval_report.json
```

Confirm:

- both generation objects have `rag_context_used: true`;
- no-RAG and with-RAG code are not automatically identical;
- Python and Java contain real Docker case results;
- `pass_rate_lift` is derived from the generated programs.

# Step 9 — Save artifacts and terminate EC2

1. Download or retain the completed Drive project.
2. Save the executed notebook.
3. Save `outputs/reports/stage5_four_arm_repository_demo.json`.
4. Save `functional_eval_report.json`.
5. In EC2, select the instance and choose **Instance state → Terminate instance**.

# Troubleshooting

## Official CodeBLEU assertion fails

Rerun Cell 0 in the corrected full-run notebook, restart the session, and
continue at Cell 0B, `Environment Verification — run after restarting`. Do not
skip Cell 0B and do not restore the old `Fraction` monkey patch.

## Corpus index says stale or incompatible

This is expected after the index redesign. Run Cell 26 with `rebuild=True` as provided.

## Repository RAG abstains in Cell 26D

Run Cell 25 again and confirm the new `policies/transfer_policy.py` and `policies/TransferPolicy.java` files were indexed.

## Docker reports permission denied under `/work`

You copied an older evaluator. Replace it with the complete inline script in Step 7. The correct script applies directory mode `0755` and file mode `0644` before the non-root container reads them.

## Adaptive policy disables a task

That means the validation run did not show a sufficient gain for that task. Do not enable it manually after inspecting test results. The repository-specific functional benchmark remains the correct place to demonstrate repository grounding.

## RAG-aware notebook says the adapter manifest is incompatible

Do not point the notebook at the v1.0 adapter and do not edit the manifest by
hand. If an interrupted attempt created an incomplete
`outputs/adapters/RepoCoderStudio_RAGAware_LoRA_v1_2` folder, remove only that
incomplete v1.2 folder and rerun the training cell. Leave
`RepoCoderStudio_FastCorrected_LoRA_v1_0` untouched because it supports the
original comparison evidence.

## Gradio says no interface is running

The old `gradio.live` link expired or the launch cell stopped. Rerun the final
Gradio cell, keep it running, and open only the new URL printed by that run.

## Docker Compose says `.env` is missing

From the project root, copy `.env.example` to `.env`, then rerun
`docker compose up --build`. Do not rename `.env.example` inside the submitted
folder; keep both files locally.

## `/api/health` names the old adapter

Stop the service and confirm that `.env`, Docker Compose or the Cloud Run
revision sets `REPOCODER_ADAPTER_NAME=RepoCoderStudio_RAGAware_LoRA_v1_2`,
`REPOCODER_PROMPT_VERSION=rag_prompt_contract_v1.2` and
`REPOCODER_TRAINING_MANIFEST_VERSION=training_manifest_rag_v1.2`. Rebuild or
redeploy after correcting the environment.

## Cloud Run starts slowly or returns 504

The first instance downloads and loads the base, embedding and reranker models.
Confirm the service has 2 CPUs, 8 GiB memory, concurrency 1 and timeout 900
seconds as shown in Part F. Inspect logs with:

```bash
gcloud run services logs read repocoder-studio --region="asia-south1" --limit=100
```

If you selected another region or service name, substitute those values. An
out-of-memory event requires more memory; an incomplete model download requires
a new revision or retry after confirming outbound access.
