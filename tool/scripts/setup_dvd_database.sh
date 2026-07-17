#!/usr/bin/env bash
# Start PostgreSQL (TEND or tool Docker) and load tool/test.sql into database "dvd".
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

TEND_ROOT="${TEND_ROOT:-/Volumes/Work/TEND}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-tend}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-tend}"
POSTGRES_ADMIN_DB="${POSTGRES_ADMIN_DB:-postgres}"
DVD_DATABASE="${DVD_DATABASE:-dvd}"
SQL_FILE="${SQL_FILE:-$TOOL_DIR/test.sql}"

USE_TEND=auto
START_DOCKER=1
FORCE_RELOAD=0
DOCKER_COMPOSE_DIR=""
DOCKER_SERVICE="postgres"

usage() {
  cat <<'EOF'
Load the Pagila DVD sample database for the AI SQL Assistant tool.

Usage:
  ./tool/scripts/setup_dvd_database.sh [options]

Options:
  --use-tend          Start/use PostgreSQL from TEND (docker compose in TEND_ROOT)
  --use-tool-docker   Start/use PostgreSQL from tool/docker-compose.yml (default fallback)
  --no-docker         Do not start Docker; connect to an already-running PostgreSQL
  --force             Drop and recreate the dvd database before loading
  --sql-file PATH     SQL dump to load (default: tool/test.sql)
  -h, --help          Show this help

Environment (defaults match /Volumes/Work/TEND):
  TEND_ROOT           Path to TEND repo (default: /Volumes/Work/TEND)
  POSTGRES_HOST       PostgreSQL host (default: localhost)
  POSTGRES_PORT       PostgreSQL port (default: 5432)
  POSTGRES_USER       PostgreSQL user (default: tend)
  POSTGRES_PASSWORD   PostgreSQL password (default: tend)
  POSTGRES_ADMIN_DB   Admin database for CREATE DATABASE (default: postgres)
  DVD_DATABASE        Target database name (default: dvd)

After loading, configure the desktop app with:
  DATABASE_URL=postgresql+psycopg://tend:tend@localhost:5432/dvd
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --use-tend) USE_TEND=1 ;;
    --use-tool-docker) USE_TEND=0 ;;
    --no-docker) START_DOCKER=0 ;;
    --force) FORCE_RELOAD=1 ;;
    --sql-file)
      SQL_FILE="$2"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
  shift
done

if [[ ! -f "$SQL_FILE" ]]; then
  echo "SQL file not found: $SQL_FILE" >&2
  exit 1
fi

if [[ "$START_DOCKER" -eq 1 ]] && ! command -v docker >/dev/null 2>&1; then
  echo "docker is required unless --no-docker is set." >&2
  exit 1
fi

USE_DOCKER_EXEC=0
if command -v psql >/dev/null 2>&1; then
  PSQL_MODE=local
elif command -v docker >/dev/null 2>&1; then
  PSQL_MODE=docker
elif [[ "$START_DOCKER" -eq 0 ]]; then
  echo "psql is required when --no-docker is set. Install PostgreSQL client tools and retry." >&2
  exit 1
else
  echo "Neither psql nor docker is available." >&2
  exit 1
fi

detect_running_postgres_compose() {
  if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx 'tool-postgres'; then
    DOCKER_COMPOSE_DIR="$TOOL_DIR"
    DOCKER_SERVICE="postgres"
    return 0
  fi

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

  PGPASSWORD="$POSTGRES_PASSWORD" pg_isready \
    -h "$POSTGRES_HOST" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_ADMIN_DB" >/dev/null 2>&1
}

wait_for_postgres() {
  echo "Waiting for PostgreSQL..."
  for _ in $(seq 1 60); do
    if pg_ready; then
      echo "PostgreSQL is ready."
      return 0
    fi
    sleep 1
  done
  echo "Timed out waiting for PostgreSQL." >&2
  return 1
}

start_tend_postgres() {
  if [[ ! -f "$TEND_ROOT/docker-compose.yml" ]]; then
    echo "TEND docker-compose not found at $TEND_ROOT" >&2
    return 1
  fi
  DOCKER_COMPOSE_DIR="$TEND_ROOT"
  DOCKER_SERVICE="postgres"
  echo "Starting PostgreSQL from TEND ($TEND_ROOT)..."
  (cd "$TEND_ROOT" && docker compose up -d postgres)
}

start_tool_postgres() {
  DOCKER_COMPOSE_DIR="$TOOL_DIR"
  DOCKER_SERVICE="postgres"
  echo "Starting PostgreSQL from tool/docker-compose.yml..."
  (cd "$TOOL_DIR" && docker compose up -d)
}

start_postgres_if_needed() {
  if [[ "$PSQL_MODE" == "local" ]] && pg_ready; then
    USE_DOCKER_EXEC=0
    echo "PostgreSQL already reachable at ${POSTGRES_HOST}:${POSTGRES_PORT}"
    return 0
  fi

  if [[ "$PSQL_MODE" == "docker" ]] && detect_running_postgres_compose && pg_ready; then
    USE_DOCKER_EXEC=1
    echo "Using running PostgreSQL container via docker compose exec."
    return 0
  fi

  if [[ "$START_DOCKER" -eq 0 ]]; then
    echo "PostgreSQL is not reachable and --no-docker was set." >&2
    return 1
  fi

  if [[ "$USE_TEND" == "1" ]]; then
    start_tend_postgres || detect_running_postgres_compose
  elif [[ "$USE_TEND" == "0" ]]; then
    if ! start_tool_postgres; then
      echo "Tool PostgreSQL could not start (port may be in use). Trying existing container..." >&2
      detect_running_postgres_compose || true
    fi
  else
    if [[ -f "$TEND_ROOT/docker-compose.yml" ]]; then
      start_tend_postgres || start_tool_postgres || detect_running_postgres_compose || true
    else
      start_tool_postgres || detect_running_postgres_compose || true
    fi
  fi

  if [[ -z "$DOCKER_COMPOSE_DIR" ]]; then
    echo "Could not start or detect a PostgreSQL container." >&2
    return 1
  fi

  USE_DOCKER_EXEC=1
  wait_for_postgres
}

run_psql_admin() {
  if [[ "$USE_DOCKER_EXEC" -eq 1 ]]; then
    (cd "$DOCKER_COMPOSE_DIR" && docker compose exec -T "$DOCKER_SERVICE" \
      psql -U "$POSTGRES_USER" -d "$POSTGRES_ADMIN_DB" "$@")
    return
  fi

  PGPASSWORD="$POSTGRES_PASSWORD" psql \
    -h "$POSTGRES_HOST" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" \
    -d "$POSTGRES_ADMIN_DB" \
    "$@"
}

run_psql_dvd() {
  if [[ "$USE_DOCKER_EXEC" -eq 1 ]]; then
    (cd "$DOCKER_COMPOSE_DIR" && docker compose exec -T "$DOCKER_SERVICE" \
      psql -U "$POSTGRES_USER" -d "$DVD_DATABASE" "$@")
    return
  fi

  PGPASSWORD="$POSTGRES_PASSWORD" psql \
    -h "$POSTGRES_HOST" \
    -p "$POSTGRES_PORT" \
    -U "$POSTGRES_USER" \
    -d "$DVD_DATABASE" \
    "$@"
}

prepare_database() {
  local exists
  exists="$(run_psql_admin -tAc "SELECT 1 FROM pg_database WHERE datname = '${DVD_DATABASE}'" || true)"

  if [[ "$exists" == "1" ]]; then
    if [[ "$FORCE_RELOAD" -eq 1 ]]; then
      echo "Dropping existing database ${DVD_DATABASE}..."
      run_psql_admin -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS ${DVD_DATABASE};"
    else
      echo "Database ${DVD_DATABASE} already exists. Skipping CREATE DATABASE."
      echo "Use --force to drop and reload from ${SQL_FILE}."
      return 0
    fi
  fi

  echo "Creating database ${DVD_DATABASE}..."
  run_psql_admin -v ON_ERROR_STOP=1 -c "CREATE DATABASE ${DVD_DATABASE};"
}

load_sql() {
  local table_count
  table_count="$(run_psql_dvd -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo 0)"

  if [[ "$table_count" -gt 0 && "$FORCE_RELOAD" -eq 0 ]]; then
    echo "Database ${DVD_DATABASE} already has ${table_count} public tables. Skipping SQL load."
    echo "Use --force to drop and reload."
    return 0
  fi

  echo "Loading ${SQL_FILE} into ${DVD_DATABASE}..."
  # pg_dump 18 meta-commands are not supported by older psql clients.
  if [[ "$USE_DOCKER_EXEC" -eq 1 ]]; then
    grep -Ev '^\\restrict |^\\unrestrict ' "$SQL_FILE" | \
      (cd "$DOCKER_COMPOSE_DIR" && docker compose exec -T "$DOCKER_SERVICE" \
        psql -U "$POSTGRES_USER" -d "$DVD_DATABASE" -v ON_ERROR_STOP=1 -f -)
  else
    grep -Ev '^\\restrict |^\\unrestrict ' "$SQL_FILE" | PGPASSWORD="$POSTGRES_PASSWORD" psql \
      -h "$POSTGRES_HOST" \
      -p "$POSTGRES_PORT" \
      -U "$POSTGRES_USER" \
      -d "$DVD_DATABASE" \
      -v ON_ERROR_STOP=1 \
      -f -
  fi
}

print_summary() {
  cat <<EOF

DVD database is ready.

Connection URL:
  postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${DVD_DATABASE}

Add this to tool/.env before first launch (or update Settings → Database):
  DATABASE_URL=postgresql+psycopg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${DVD_DATABASE}

Sample tables: actor, film, customer, rental, payment, store, inventory
EOF
}

start_postgres_if_needed
prepare_database
load_sql
print_summary
