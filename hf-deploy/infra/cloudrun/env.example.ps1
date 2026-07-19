# Copy to env.ps1, fill in, then from this directory:
#   . .\env.ps1
#   bash ./deploy.sh
#
# env.ps1 is gitignored — never commit project id, URL, or secrets.
#
# Requires: Google Cloud SDK (gcloud) and bash (Git Bash or WSL) for deploy.sh.
# Variables set here are inherited by bash when you run deploy.sh in the same shell.

$env:GCP_PROJECT_ID = "your-gcp-project-id"
$env:GCP_REGION = "asia-south2"  # Hyderabad
$env:SERVICE_NAME = "codegen-api"
$env:AR_REPO = "hf-deploy"

# Set after first deploy (deploy.sh updates env.sh on Unix; set manually in env.ps1 on Windows)
$env:CLOUD_RUN_SERVICE_URL = "https://***.asia-south2.run.app"

# Cloud Run sizing (350M model + PyTorch needs ample RAM on CPU)
$env:CLOUD_RUN_MEMORY = "8Gi"
$env:CLOUD_RUN_CPU = "2"
$env:CLOUD_RUN_TIMEOUT = "900"
$env:CLOUD_RUN_MIN_INSTANCES = "0"
$env:CLOUD_RUN_MAX_INSTANCES = "1"

# Hugging Face (public adapters — token usually not required)
$env:HF_ORG = "care2achieve"

# Optional: VERBOSE=1 for gcloud debug output during deploy
# $env:VERBOSE = "1"
