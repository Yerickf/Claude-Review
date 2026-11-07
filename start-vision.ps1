# Arranca a câmara e envia os eventos para o servidor.
# Exemplos:   .\start-vision.ps1 --show --print
#             .\start-vision.ps1 --cam 1 --show
Set-Location $PSScriptRoot
uv run python -m vision.run @args
