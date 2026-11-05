<#
.SYNOPSIS
  Aplica no GitHub o que docs/github/README.md e scripts/github_repos.json descrevem. Idempotente.
  Sem -Abrir: perfil (nome, bio, blog, local), repositório mateusrfabro/mateusrfabro com o README,
  descrição e topics dos 24 repositórios. Com -Abrir: muda a visibilidade para public SÓ dos repos com
  abre=true E marcados "ABRE" no relatório do Plano B.
.PARAMETER Abrir
  Abre os repositórios (irreversível na prática: histórico fica público).
#>
param([switch]$Abrir, [switch]$SoMostrar)
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
[Console]::OutputEncoding = [Text.Encoding]::UTF8
$repos = Get-Content (Join-Path $raiz "scripts\github_repos.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$relatorio = "C:\Users\mateu\Projects\_fora-do-git\relatorios\2026-11-repos-estado.md"
$perfilRepo = "C:\Users\mateu\Projects\mateusrfabro"

function Passo($msg) { Write-Host ("== " + $msg) -ForegroundColor Cyan }

Passo "1. Perfil"
$antes = gh api user --jq '{name,bio,blog,location}'
Write-Host "antes:  $antes"
if (-not $SoMostrar) {
  gh api -X PATCH /user -f name="Mateus Fabro" `
    -f bio="Engenheiro de Dados & Analytics - construo o pipeline e o produto em volta dele (Python, SQL, TypeScript). Em busca de vaga." `
    -f blog="https://mateusfabro.vercel.app" -f location="Londrina, PR - Brasil" | Out-Null
  Write-Host "depois: $(gh api user --jq '{name,bio,blog,location}')"
}

Passo "2. Repositório de perfil mateusrfabro/mateusrfabro"
$ErrorActionPreference = "Continue"   # no 5.1, 2>$null + Stop transforma o stderr do gh em exceção
gh repo view mateusrfabro/mateusrfabro --json name 2>$null | Out-Null
$existe = ($LASTEXITCODE -eq 0)
$ErrorActionPreference = "Stop"
if (-not $SoMostrar) {
  if (-not $existe) { gh repo create mateusrfabro/mateusrfabro --public --description "Perfil" | Out-Null }
  if (-not (Test-Path $perfilRepo)) { git clone https://github.com/mateusrfabro/mateusrfabro.git $perfilRepo | Out-Null }
  Copy-Item (Join-Path $raiz "docs\github\README.md") (Join-Path $perfilRepo "README.md") -Force
  Push-Location $perfilRepo
  git config user.email mateusrfabro@hotmail.com
  git add README.md
  $mudou = git status --porcelain
  if ($mudou) { git commit -q -m "perfil: README gerado de diario-mateus-fabro"; git push -q origin HEAD }
  Pop-Location
  Write-Host "README publicado: https://github.com/mateusrfabro"
} else { Write-Host "repo existe: $existe" }

Passo "3. Descrição e topics dos $($repos.Count) repositórios"
foreach ($r in $repos) {
  $atual = gh repo view "mateusrfabro/$($r.nome)" --json description,repositoryTopics,visibility | ConvertFrom-Json
  $topicsAtuais = @($atual.repositoryTopics | ForEach-Object { $_.name })
  Write-Host ("{0,-32} {1,-8} '{2}'" -f $r.nome, $atual.visibility, $atual.description)
  if ($SoMostrar) { continue }
  if ($atual.description -ne $r.descricao) { gh repo edit "mateusrfabro/$($r.nome)" --description $r.descricao | Out-Null }
  foreach ($t in $r.topics) { if ($topicsAtuais -notcontains $t) { gh repo edit "mateusrfabro/$($r.nome)" --add-topic $t | Out-Null } }
}

if ($Abrir) {
  Passo "4. Abrir repositórios"
  if (-not (Test-Path $relatorio)) { throw "relatório do Plano B ausente: $relatorio" }
  $linhas = Get-Content $relatorio -Encoding UTF8
  foreach ($r in $repos | Where-Object { $_.abre }) {
    $marca = $linhas | Where-Object { $_ -match ("^\|\s*" + [regex]::Escape($r.nome) + "\s*\|.*\|\s*ABRE\s*\|") }
    if (-not $marca) { Write-Host "NÃO ABRE (sem marca ABRE no relatório): $($r.nome)" -ForegroundColor Yellow; continue }
    gh repo edit "mateusrfabro/$($r.nome)" --visibility public --accept-visibility-change-consequences | Out-Null
    Write-Host "ABERTO: https://github.com/mateusrfabro/$($r.nome)" -ForegroundColor Green
  }
}
Write-Host "fim."
