# Arranca o servidor e o palco.   .\start.ps1
# Com -Lan, outros dispositivos da mesma rede (ex.: um telemóvel) também conseguem aceder.
param([switch]$Lan)
Set-Location $PSScriptRoot
uv run python tools/build_content.py
$addr = if ($Lan) { "0.0.0.0" } else { "127.0.0.1" }
Write-Host "Palco: http://localhost:8000/stage/   (Ctrl+C para parar; F = ecrã inteiro; D = debug)"
uv run uvicorn server.main:app --host $addr --port 8000
