$ErrorActionPreference = 'Stop'
$envFile = Join-Path $PSScriptRoot '.env'
$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $envFile)) {
    throw 'Falta .env. Copiá .env.example a .env y completá las claves locales.'
}
if (-not (Test-Path -LiteralPath $python)) {
    throw 'Falta .venv. Ejecutá: py -m venv .venv; .venv\Scripts\python -m pip install -e ".[dev]"'
}

foreach ($line in Get-Content -LiteralPath $envFile) {
    if ($line -match '^\s*#' -or [string]::IsNullOrWhiteSpace($line)) { continue }
    if ($line -notmatch '^([A-Z][A-Z0-9_]*)=(.*)$') { continue }
    $name = $Matches[1]
    $value = $Matches[2].Trim()
    if ($value.Length -ge 2 -and (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'")))) {
        $value = $value.Substring(1, $value.Length - 2)
    }
    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
}

if (-not $env:JARVIS_API_KEY) {
    throw 'Completá JARVIS_API_KEY en .env antes de iniciar.'
}

Write-Host 'Jarvis disponible en http://127.0.0.1:8010/demo'
Write-Host 'Presioná Ctrl+C para detenerlo.'
& $python -m uvicorn jarvis_noc.main:app --host 127.0.0.1 --port 8010
