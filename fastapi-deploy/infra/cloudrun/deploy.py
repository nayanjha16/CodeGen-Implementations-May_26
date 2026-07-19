#!/usr/bin/env python3
"""Build and deploy codegen-api to Google Cloud Run.

Cross-platform: the same file works on Windows, macOS, and Linux (it shells out
to the `gcloud` CLI, which behaves identically on every OS).

Usage (from anywhere):

    # 1) one-time: copy env.example -> deploy.env and set GCP_PROJECT_ID
    # 2) authenticate once:  gcloud auth login
    python fastapi-deploy/infra/cloudrun/deploy.py

Config is read from (last wins): built-in defaults -> deploy.env file next to
this script -> real environment variables. `deploy.env` is gitignored.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEPLOY_ROOT = SCRIPT_DIR.parent.parent  # fastapi-deploy/

# On Windows `gcloud` is a .CMD batch file, which subprocess cannot launch by
# bare name (no shell). Resolve the full path once so every call works on
# Windows, macOS, and Linux.
GCLOUD = shutil.which("gcloud") or "gcloud"

DEFAULTS = {
    "GCP_REGION": "asia-south2",  # Hyderabad
    "SERVICE_NAME": "codegen-api",
    "AR_REPO": "codegen-api",
    "IMAGE_TAG": "latest",
    "CLOUD_RUN_MEMORY": "8Gi",
    "CLOUD_RUN_CPU": "2",
    "CLOUD_RUN_TIMEOUT": "900",
    "CLOUD_RUN_MIN_INSTANCES": "0",
    "CLOUD_RUN_MAX_INSTANCES": "1",
    "HF_ORG": "codegenstudio",
}


def load_env() -> dict[str, str]:
    cfg = dict(DEFAULTS)
    env_file = SCRIPT_DIR / "deploy.env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            cfg[key.strip()] = value.strip().strip('"').strip("'")
    # Real environment variables override the file.
    for key in list(cfg) + ["GCP_PROJECT_ID", "CLOUD_RUN_SERVICE_URL"]:
        if os.getenv(key):
            cfg[key] = os.environ[key]
    return cfg


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("+ " + " ".join(cmd))
    return subprocess.run(cmd, check=check)


def main() -> int:
    if shutil.which("gcloud") is None:
        print("ERROR: gcloud CLI not found. Install it and run `gcloud auth login`.")
        print("  Windows: winget install Google.CloudSDK")
        print("  macOS:   brew install --cask google-cloud-sdk")
        return 2

    cfg = load_env()
    project = cfg.get("GCP_PROJECT_ID")
    if not project:
        print("ERROR: GCP_PROJECT_ID not set. Copy env.example to deploy.env and set it.")
        return 2

    region = cfg["GCP_REGION"]
    service = cfg["SERVICE_NAME"]
    repo = cfg["AR_REPO"]
    tag = cfg["IMAGE_TAG"]
    image = f"{region}-docker.pkg.dev/{project}/{repo}/{service}:{tag}"

    print(f"Project:  {project}")
    print(f"Region:   {region}")
    print(f"Service:  {service}")
    print(f"Image:    {image}\n")

    run([GCLOUD, "config", "set", "project", project])

    describe = subprocess.run(
        [GCLOUD, "artifacts", "repositories", "describe", repo, f"--location={region}"],
        capture_output=True,
    )
    if describe.returncode != 0:
        run([
            GCLOUD, "artifacts", "repositories", "create", repo,
            "--repository-format=docker", f"--location={region}",
            "--description=codegen-api images",
        ])

    run([GCLOUD, "auth", "configure-docker", f"{region}-docker.pkg.dev", "--quiet"])

    run([
        GCLOUD, "builds", "submit", str(DEPLOY_ROOT),
        "--config", str(DEPLOY_ROOT / "cloudbuild.yaml"),
        f"--substitutions=_IMAGE={image}",
    ])

    run([
        GCLOUD, "run", "deploy", service,
        "--image", image,
        "--region", region,
        "--platform", "managed",
        "--allow-unauthenticated",
        "--memory", cfg["CLOUD_RUN_MEMORY"],
        "--cpu", cfg["CLOUD_RUN_CPU"],
        "--timeout", cfg["CLOUD_RUN_TIMEOUT"],
        "--min-instances", cfg["CLOUD_RUN_MIN_INSTANCES"],
        "--max-instances", cfg["CLOUD_RUN_MAX_INSTANCES"],
        "--port", "8080",
        "--cpu-boost",
        "--startup-probe",
        "initialDelaySeconds=30,timeoutSeconds=10,periodSeconds=10,"
        "failureThreshold=36,httpGet.path=/health,httpGet.port=8080",
        "--set-env-vars",
        f"CODEGEN_ADAPTER_SOURCE=hub,HF_ORG={cfg['HF_ORG']},"
        "CODEGEN_DEVICE=cpu,CODEGEN_EAGER_LOAD=true,PYTHONPATH=/app",
    ])

    url = subprocess.run(
        [GCLOUD, "run", "services", "describe", service,
         "--region", region, "--format=value(status.url)"],
        capture_output=True, text=True,
    ).stdout.strip()

    print(f"\nDeployed: {url}")
    print(f"Health:   {url}/health")
    print(f"Cursor:   {url}/v1  (model: codegen-multi-adapter)")
    print("Save this URL as CLOUD_RUN_SERVICE_URL in deploy.env (gitignored).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
