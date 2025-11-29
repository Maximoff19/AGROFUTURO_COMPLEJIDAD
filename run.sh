#!/usr/bin/env bash
# Bootstrap and run AgroFuturo backend (and optional frontend) on any machine.
# Uso:
#   ./run.sh           # levanta backend en http://localhost:8000
#   ./run.sh frontend  # sirve el frontend estático en http://localhost:8080

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${ROOT_DIR}/.venv"
REQ_FILE="${ROOT_DIR}/backend/requirements.txt"
APP_PATH="backend.main:app"
BACKEND_PORT="${PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-8080}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 no está instalado en PATH." >&2
  exit 1
fi

# Crea el entorno si no existe y asegura dependencias instaladas
if [ ! -d "${VENV}" ]; then
  python3 -m venv "${VENV}"
fi
# shellcheck disable=SC1091
source "${VENV}/bin/activate"
pip install --upgrade pip
pip install -r "${REQ_FILE}"

case "${1:-}" in
  frontend)
    cd "${ROOT_DIR}/FRONTEND"
    echo "Frontend en http://localhost:${FRONTEND_PORT}"
    python3 -m http.server "${FRONTEND_PORT}"
    ;;
  *)
    cd "${ROOT_DIR}"
    echo "Backend en http://localhost:${BACKEND_PORT} (docs en /docs)"
    uvicorn "${APP_PATH}" --reload --port "${BACKEND_PORT}"
    ;;
esac
