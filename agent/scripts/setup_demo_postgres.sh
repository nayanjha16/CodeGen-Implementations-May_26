#!/usr/bin/env bash
# Load agent/data/dvd/test.sql into PostgreSQL database "dvd" (standalone demo).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$AGENT_DIR/.." && pwd)"

TEND_ROOT="${TEND_ROOT:-$REPO_ROOT/../TEND}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-tend}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-tend}"
POSTGRES_ADMIN_DB="${POSTGRES_ADMIN_DB:-postgres}"
DEMO_DATABASE="${AGENT_DEMO_POSTGRES_DATABASE:?Set AGENT_DEMO_POSTGRES_DATABASE before running this script}"
SQL_FILE="${AGENT_DEMO_SQL_DUMP:?Set AGENT_DEMO_SQL_DUMP to your .sql dump path}"

USE_TEND=auto
START_DOCKER=1
FORCE_RELOAD=0
DOCKER_COMPOSE_DIR=""
DOCKER_SERVICE="postgres"

usage() {
  cat <<EOF
Load agent demo SQL into PostgreSQL (your custom database — set AGENT_DEMO_* env vars first).

Usage:
  ./agent/scripts/setup_demo_postgres.sh [options]

Options:
  --use-tend          Use TEND docker compose postgres
  --no-docker         Connect to already-running Postgres
  --force             Drop and recreate demo database before load
  --sql-file PATH     SQL dump (required via AGENT_DEMO_SQL_DUMP or --sql-file)
  -h, --help          Show help

Environment:
  AGENT_DEMO_POSTGRES_DATABASE   Target DB name (default: dvd)
  AGENT_DEMO_SQL_DUMP            Path to SQL file
  TEND_ROOT                      TEND repo path
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --use-tend) USE_TEND=1 ;;
    --no-docker) START_DOCKER=0 ;;
    --force) FORCE_RELOAD=1 ;;
    --sql-file) SQL_FILE="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 1 ;;
  esac
  shift
done

if [[ ! -f "$SQL_FILE" ]]; then
  echo "SQL file not found: $SQL_FILE" >&2
  echo "See agent/data/README.md — pick a database and export or download a .sql dump first." >&2
  exit 1
fi

if command -v psql >/dev/null 2>&1; then
  PSQL_MODE=local
elif command -v docker >/dev/null 2>&1; then
  PSQL_MODE=docker
else
  echo "Need psql or docker." >&2
  exit 1
fi

detect_running_postgres_compose() {
  if [[ -f "$TEND_ROOT/docker-compose.yml" ]]; then
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -Eiq 'tend-postgres-1|tend_postgres_1'; then
      DOCKER_COMPOSE_DIR="$TEND_ROOT"
      DOCKER_SERVICE="postgres"
      return 0
    fi
  fi
  return 1
}

pg_ready() {
  if [[ "$PSQL_MODE" == "docker" && -n "$DOCKER_COMPOSE_DIR" ]]; then
    (cd "$DOCKER_COMPOSE_DIR" && docker compose exec -T "$DOCKER_SERVICE" \
      pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_ADMIN_DB") >/dev/null 2>&1
    return $?
  fi
  PGPASSWORD="$POSTGRES_PASSWORD" pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" -d "$POSTGRES_ADMIN_DB" >/dev/null 2>&1
}

start_postgres_if_needed() {
  if [[ "$PSQL_MODE" == "local" ]] && pg_ready; then return 0; fi
  if [[ "$PSQL_MODE" == "docker" ]] && detect_running_postgres_compose && pg_ready; then return 0; fi
  if [[ "$START_DOCKER" -eq 0 ]]; then
    echo "Postgres not reachable and --no-docker set." >&2
    exit 1
  fi
  if [[ -f "$TEND_ROOT/docker-compose.yml" ]]; then
    (cd "$TEND_ROOT" && docker compose up -d postgres)
    DOCKER_COMPOSE_DIR="$TEND_ROOT"
    DOCKER_SERVICE="postgres"
  else
    echo "TEND docker-compose not found at $TEND_ROOT" >&2
    exit 1
  fi
  for _ in $(seq 1 60); do pg_ready && return 0; sleep 1; done
  echo "Timed out waiting for Postgres." >&2
  exit 1
}

run_psql_admin() {
  if [[ -n "$DOCKER_COMPOSE_DIR" ]]; then
    (cd "$DOCKER_COMPOSE_DIR" && docker compose exec -T "$DOCKER_SERVICE" \
      psql -U "$POSTGRES_USER" -d "$POSTGRES_ADMIN_DB" "$@")
  else
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" \
      -U "$POSTGRES_USER" -d "$POSTGRES_ADMIN_DB" "$@"
  fi
}

run_psql_demo() {
  if [[ -n "$DOCKER_COMPOSE_DIR" ]]; then
    (cd "$DOCKER_COMPOSE_DIR" && docker compose exec -T "$DOCKER_SERVICE" \
      psql -U "$POSTGRES_USER" -d "$DEMO_DATABASE" "$@")
  else
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" \
      -U "$POSTGRES_USER" -d "$DEMO_DATABASE" "$@"
  fi
}

prepare_database() {
  local exists
  exists="$(run_psql_admin -tAc "SELECT 1 FROM pg_database WHERE datname = '${DEMO_DATABASE}'" || true)"
  if [[ "$exists" == "1" ]]; then
    if [[ "$FORCE_RELOAD" -eq 1 ]]; then
      run_psql_admin -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS ${DEMO_DATABASE};"
    else
      echo "Database ${DEMO_DATABASE} exists. Use --force to drop and reload."
      return 0
    fi
  fi
  run_psql_admin -v ON_ERROR_STOP=1 -c "CREATE DATABASE ${DEMO_DATABASE};"
}

load_sql() {
  local table_count
  table_count="$(run_psql_demo -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo 0)"
  if [[ "$table_count" -gt 0 && "$FORCE_RELOAD" -eq 0 ]]; then
    echo "Database ${DEMO_DATABASE} already has ${table_count} public tables. Skipping load."
    return 0
  fi
  echo "Loading ${SQL_FILE} into ${DEMO_DATABASE}..."
  if [[ -n "$DOCKER_COMPOSE_DIR" ]]; then
    grep -Ev '^\\restrict |^\\unrestrict ' "$SQL_FILE" | \
      (cd "$DOCKER_COMPOSE_DIR" && docker compose exec -T "$DOCKER_SERVICE" \
        psql -U "$POSTGRES_USER" -d "$DEMO_DATABASE" -v ON_ERROR_STOP=1 -f -)
  else
    grep -Ev '^\\restrict |^\\unrestrict ' "$SQL_FILE" | PGPASSWORD="$POSTGRES_PASSWORD" psql \
      -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$DEMO_DATABASE" \
      -v ON_ERROR_STOP=1 -f -
  fi
}

start_postgres_if_needed
prepare_database
load_sql
echo ""
echo "Demo Postgres ready: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${DEMO_DATABASE}"
echo "Set AGENT_DB_PROFILE=standalone in agent/.env for the agent."
