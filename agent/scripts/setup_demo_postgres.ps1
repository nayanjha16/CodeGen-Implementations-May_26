# Load your custom demo SQL into PostgreSQL. Set AGENT_DEMO_* env vars first.
param(
    [switch]$UseTend,
    [switch]$Force,
    [string]$SqlFile = "",
    [string]$Database = $(if ($env:AGENT_DEMO_POSTGRES_DATABASE) { $env:AGENT_DEMO_POSTGRES_DATABASE } else { $env:AGENT_DEMO_DB_ID }),
    [string]$TendRoot = $(if ($env:TEND_ROOT) { $env:TEND_ROOT } else { Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) "TEND" })
)

$ErrorActionPreference = "Stop"
if (-not $Database) {
    Write-Error "Set AGENT_DEMO_DB_ID (e.g. northwind) before running this script."
}
if (-not $SqlFile) {
    $SqlFile = $env:AGENT_DEMO_SQL_DUMP
}
if (-not $SqlFile) {
    Write-Error "Set AGENT_DEMO_SQL_DUMP to your .sql file path. See agent\data\README.md"
}
if (-not (Test-Path $SqlFile)) {
    Write-Error "SQL file not found: $SqlFile"
}

$pgUser = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "tend" }
$pgPass = if ($env:POSTGRES_PASSWORD) { $env:POSTGRES_PASSWORD } else { "tend" }
$pgHost = if ($env:POSTGRES_HOST) { $env:POSTGRES_HOST } else { "localhost" }
$pgPort = if ($env:POSTGRES_PORT) { $env:POSTGRES_PORT } else { "5432" }

function Invoke-PsqlAdmin([string[]]$Args) {
    $container = docker ps --format "{{.Names}}" | Where-Object { $_ -match "tend-postgres|tend_postgres" } | Select-Object -First 1
    if ($container) {
        docker exec -i $container psql -U $pgUser -d postgres @Args
        return
    }
    $env:PGPASSWORD = $pgPass
    & psql -h $pgHost -p $pgPort -U $pgUser -d postgres @Args
}

function Invoke-PsqlDemo([string[]]$Args) {
    $container = docker ps --format "{{.Names}}" | Where-Object { $_ -match "tend-postgres|tend_postgres" } | Select-Object -First 1
    if ($container) {
        docker exec -i $container psql -U $pgUser -d $Database @Args
        return
    }
    $env:PGPASSWORD = $pgPass
    & psql -h $pgHost -p $pgPort -U $pgUser -d $Database @Args
}

if ($UseTend -and (Test-Path (Join-Path $TendRoot "docker-compose.yml"))) {
    Push-Location $TendRoot
    docker compose up -d postgres
    Pop-Location
    Start-Sleep -Seconds 3
}

$exists = Invoke-PsqlAdmin @("-tAc", "SELECT 1 FROM pg_database WHERE datname = '$Database'")
if ($exists -match "1") {
    if ($Force) {
        Invoke-PsqlAdmin @("-v", "ON_ERROR_STOP=1", "-c", "DROP DATABASE IF EXISTS $Database;")
        Invoke-PsqlAdmin @("-v", "ON_ERROR_STOP=1", "-c", "CREATE DATABASE $Database;")
    }
} else {
    Invoke-PsqlAdmin @("-v", "ON_ERROR_STOP=1", "-c", "CREATE DATABASE $Database;")
}

$tableCount = Invoke-PsqlDemo @("-tAc", "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
if ($tableCount -match "^\s*0\s*$" -or $Force) {
    Write-Host "Loading $SqlFile into $Database ..."
    $container = docker ps --format "{{.Names}}" | Where-Object { $_ -match "tend-postgres|tend_postgres" } | Select-Object -First 1
    $filtered = Get-Content $SqlFile | Where-Object { $_ -notmatch '^\\restrict |^\\unrestrict ' }
    if ($container) {
        $filtered | docker exec -i $container psql -U $pgUser -d $Database -v ON_ERROR_STOP=1
    } else {
        $env:PGPASSWORD = $pgPass
        $filtered | & psql -h $pgHost -p $pgPort -U $pgUser -d $Database -v ON_ERROR_STOP=1
    }
} else {
    Write-Host "Database $Database already has tables. Use -Force to reload."
}

Write-Host ""
Write-Host "Demo Postgres ready: postgresql://${pgUser}:${pgPass}@${pgHost}:${pgPort}/${Database}"
Write-Host "Set AGENT_DB_PROFILE=standalone and matching AGENT_DEMO_* in agent/.env"
