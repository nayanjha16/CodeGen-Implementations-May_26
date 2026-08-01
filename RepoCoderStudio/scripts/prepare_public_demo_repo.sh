#!/usr/bin/env bash
set -euo pipefail

destination="${1:-repo_explorer_data/public_demo/aws_sdk_s3}"
repository_url="https://github.com/awsdocs/aws-doc-sdk-examples.git"

if [[ -e "${destination}" ]]; then
  echo "Destination already exists; refusing to overwrite: ${destination}" >&2
  exit 2
fi

mkdir -p "$(dirname "${destination}")"

git clone --filter=blob:none --no-checkout "${repository_url}" "${destination}"
git -C "${destination}" sparse-checkout init --cone
git -C "${destination}" sparse-checkout set \
  python/example_code/s3 \
  javav2/example_code/s3
git -C "${destination}" checkout main

commit_sha="$(git -C "${destination}" rev-parse HEAD)"
{
  echo "repository=${repository_url}"
  echo "commit=${commit_sha}"
  echo "subtrees=python/example_code/s3,javav2/example_code/s3"
  echo "license=Apache-2.0"
} > "${destination}/REPOCODER_PROVENANCE.txt"

echo "Prepared ${destination}"
echo "Pinned commit: ${commit_sha}"
echo "Set REPOCODER_REPO_PATH=${destination} before importing src.config."
