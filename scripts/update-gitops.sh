#!/usr/bin/env bash
set -euo pipefail

GITOPS_ROOT="${1:?GitOps repo path required}"
IMAGE_TAG="${2:?Image tag required}"

for env in dev qa prd; do
  values_file="${GITOPS_ROOT}/flask-aws-monitor/${env}/values.yaml"
  if [[ ! -f "${values_file}" ]]; then
    echo "Missing values file: ${values_file}"
    exit 1
  fi
  sed -i.bak -E "s/^([[:space:]]*tag:[[:space:]]*).*/\1\"${IMAGE_TAG}\"/" "${values_file}"
  rm -f "${values_file}.bak"
  echo "Updated ${values_file} -> tag: ${IMAGE_TAG}"
done
