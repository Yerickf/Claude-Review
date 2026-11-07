# Prepara tudo de uma vez. Corre dentro da pasta do projeto:   .\setup.ps1
# Podes correr várias vezes: só faz o que ainda falta.
param([switch]$SkipGitHub)

$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot

function Step($t) { Write-Host ""; Write-Host "==> $t" -ForegroundColor Cyan }
function Ok($t)   { Write-Host "    OK  $t" -ForegroundColor Green }
function Warn($t) { Write-Host "    !!  $t" -ForegroundColor Yellow }
function Have($c) { return [bool](Get-Command $c -ErrorAction SilentlyContinue) }
function Refresh-Path {
    $m = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $u = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$m;$u"
}

Step "1/6  Ferramentas (winget)"
if (-not (Have "winget")) {
    Warn "O winget não existe. Atualiza o 'Instalador de Aplicações' na Microsoft Store e volta a correr."
    exit 1
}
$tools = @(
    @{ cmd = "git"; id = "Git.Git" },
    @{ cmd = "uv";  id = "astral-sh.uv" },
    @{ cmd = "gh";  id = "GitHub.cli" },
    @{ cmd = "code"; id = "Microsoft.VisualStudioCode" }
)
foreach ($t in $tools) {
    if (Have $t.cmd) { Ok $t.cmd; continue }
    Write-Host "    a instalar $($t.id) ..."
    winget install --id $t.id -e --accept-source-agreements --accept-package-agreements
}
Refresh-Path
$missing = @()
foreach ($c in @("git", "uv", "gh")) { if (-not (Have $c)) { $missing += $c } }
if ($missing.Count -gt 0) {
    Warn "Instalado, mas este terminal ainda não vê: $($missing -join ', ')."
    Warn "Fecha este terminal, abre outro nesta pasta e volta a correr  .\setup.ps1"
    exit 0
}

Step "2/6  Python e bibliotecas (uv)"
uv python install 3.12
uv sync
if ($LASTEXITCODE -ne 0) { Warn "O 'uv sync' falhou. Lê a mensagem acima."; exit 1 }
uv run python tools/check_env.py
if ($LASTEXITCODE -ne 0) { Warn "Há problemas no ambiente Python (ver acima)."; exit 1 }

Step "3/6  Marcadores e conteúdo"
uv run python tools/make_markers.py
uv run python tools/build_content.py

Step "4/6  Testes rápidos"
uv run python -m vision.dial
uv run python -m tests.test_hub
uv run python -m tests.test_bus
if ($LASTEXITCODE -ne 0) { Warn "Algum teste falhou. Diz-me qual foi." } else { Ok "testes passaram" }

Step "5/6  Git"
if (-not (Test-Path ".git")) { git init -b main | Out-Null; Ok "repositório criado" } else { Ok "o repositório já existe" }
$name = git config user.name
if (-not $name) { $name = Read-Host "    Nome para os commits"; git config user.name "$name" }
$mail = git config user.email
if (-not $mail) { $mail = Read-Host "    Email para os commits"; git config user.email "$mail" }
git add -A
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) { git commit -m "Estrutura inicial do projeto" | Out-Null; Ok "primeiro commit feito" } else { Ok "nada de novo para guardar" }

Step "6/6  GitHub"
if ($SkipGitHub) {
    Warn "Ignorado (-SkipGitHub). Mais tarde: gh auth login  e depois  .\setup.ps1"
} else {
    gh auth status *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    Vai aparecer um CÓDIGO neste terminal."
        Write-Host "    Escreve-o em https://github.com/login/device (podes fazê-lo no telemóvel)."
        gh auth login -h github.com -p https -w
    }
    gh auth status *> $null
    if ($LASTEXITCODE -ne 0) {
        Warn "Sem sessão no GitHub. Quando conseguires:  gh auth login  e volta a correr  .\setup.ps1"
    } else {
        git remote get-url origin *> $null
        if ($LASTEXITCODE -eq 0) {
            git push -u origin main
            Ok "enviado para o GitHub"
        } else {
            gh repo create tabuleiro-vivo --private --source=. --remote=origin --push
            if ($LASTEXITCODE -ne 0) {
                Warn "Não consegui criar o repositório (talvez já exista com esse nome)."
                Warn "Se já existe, apaga esta pasta e faz:  gh repo clone tabuleiro-vivo"
            } else {
                Ok "repositório criado e enviado"
            }
        }
    }
}

Write-Host ""
Write-Host "Pronto. Próximos passos estão em docs\TODO.md" -ForegroundColor Green
Write-Host "  1. Imprime tools\marcadores.pdf (tamanho real, 100%)"
Write-Host "  2. Convida o teu colega: GitHub > repositório > Settings > Collaborators"
Write-Host "  3. Abre o palco:  .\start.ps1   e vai a http://localhost:8000/stage/  (teclas 1-7, setas, 0)"
Write-Host "  4. Se este PC é partilhado, no fim:  gh auth logout"
