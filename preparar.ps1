$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$envFile = Join-Path $root '.env'
if (Test-Path -LiteralPath $envFile) {
    Write-Output '.env ya existe. No se modificó.'
    exit 0
}

$bytes = [byte[]]::new(32)
[Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
$localKey = [Convert]::ToBase64String($bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
$content = Get-Content -LiteralPath (Join-Path $root '.env.example') -Raw
$content = $content -replace '(?m)^JARVIS_API_KEY=[^\r\n]*', "JARVIS_API_KEY=$localKey"
[IO.File]::WriteAllText($envFile, $content, [Text.UTF8Encoding]::new($false))
Write-Output '.env creado. La clave local está en JARVIS_API_KEY dentro de ese archivo.'
