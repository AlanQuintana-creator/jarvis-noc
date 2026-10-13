$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile = Join-Path $root '.env'

if (-not (Test-Path -LiteralPath $envFile)) {
    Write-Error 'Falta .env. Ejecutá primero preparar.ps1.'
}

$secret = Read-Host 'Pegá tu API key de Groq (no se mostrará)' -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
try {
    $apiKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
}

if ([string]::IsNullOrWhiteSpace($apiKey) -or $apiKey.Length -lt 20 -or $apiKey -match '[\r\n]') {
    Write-Error 'La clave parece incompleta. Copiá la API key completa desde GroqCloud.'
}

$lines = Get-Content -LiteralPath $envFile
$lines = $lines | ForEach-Object {
    if ($_ -match '^JARVIS_MODEL_API_KEY=') { "JARVIS_MODEL_API_KEY=$apiKey" }
    elseif ($_ -match '^JARVIS_STT_API_KEY=') { "JARVIS_STT_API_KEY=$apiKey" }
    else { $_ }
}
[IO.File]::WriteAllLines($envFile, [string[]]$lines, [Text.UTF8Encoding]::new($false))
$apiKey = $null
Write-Output 'Clave guardada en .env. Reiniciá Jarvis con: docker compose up -d --build'
