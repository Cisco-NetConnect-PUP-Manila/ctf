$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$envPath = Join-Path $root ".env"
$examplePath = Join-Path $root ".env.example"

function Read-EnvFile {
  param([string]$Path)

  $values = @{}
  if (-not (Test-Path -LiteralPath $Path)) {
    return $values
  }

  foreach ($line in Get-Content -LiteralPath $Path) {
    $trimmed = $line.Trim()
    if (-not $trimmed -or $trimmed.StartsWith("#") -or -not $trimmed.Contains("=")) {
      continue
    }

    $parts = $trimmed.Split("=", 2)
    $values[$parts[0]] = $parts[1]
  }

  return $values
}

function Get-Value {
  param(
    [hashtable]$Values,
    [string]$Key,
    [string]$Default
  )

  if ($Values.ContainsKey($Key) -and $Values[$Key]) {
    return $Values[$Key]
  }

  return $Default
}

$values = Read-EnvFile -Path $envPath
if ($values.Count -eq 0) {
  $values = Read-EnvFile -Path $examplePath
}

$frontendPort = Get-Value $values "FRONTEND_PORT" "3001"
$backendPort = Get-Value $values "BACKEND_PORT" "8001"
$postgresPort = Get-Value $values "POSTGRES_PORT" "5433"

Write-Host "Packet Capture local URLs:"
Write-Host "  Frontend:     http://localhost:$frontendPort"
Write-Host "  Backend docs: http://localhost:$backendPort/docs"
Write-Host "  API health:   http://localhost:$backendPort/health"
Write-Host "  DB health:    http://localhost:$backendPort/health/db"
Write-Host "  PostgreSQL:   localhost:$postgresPort"
Write-Host ""

Push-Location $root
try {
  $previousErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  $statusOutput = & cmd.exe /c "docker-compose ps 2>&1"
  $composeExitCode = $LASTEXITCODE
  $ErrorActionPreference = $previousErrorActionPreference

  if ($composeExitCode -eq 0) {
    $statusOutput
  }
  else {
    Write-Host "Docker status unavailable. Make sure Docker Desktop is running, then run:"
    Write-Host "  docker-compose ps"
  }
}
finally {
  Pop-Location
}
