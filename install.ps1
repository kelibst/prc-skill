<#
.SYNOPSIS
  Install the PRC coordinator suite without the plugin system (Windows PowerShell 5.1+ / pwsh).
.EXAMPLE
  .\install.ps1             # install into ~\.claude (all projects)
  .\install.ps1 -Project    # install into .\.claude of the current directory
  .\install.ps1 -Uninstall  # remove it (add -Project for a project install)
  .\install.ps1 -DryRun     # show what would happen, change nothing
#>
param([switch]$Project, [switch]$Uninstall, [switch]$DryRun)
$ErrorActionPreference = 'Stop'

$Src = Join-Path $PSScriptRoot 'plugins\prc'
$Home_ = if ($env:CLAUDE_CONFIG_DIR) { $env:CLAUDE_CONFIG_DIR } else { Join-Path $HOME '.claude' }
$Target = if ($Project) { Join-Path (Get-Location) '.claude' } else { $Home_ }
$Skills = @('project-coordinator')
$Commands = Get-ChildItem (Join-Path $Src 'commands') -Filter 'prc-*.md' | ForEach-Object Name
$Backup = Join-Path $Home_ ("backups\prc-" + (Get-Date -Format 'yyyyMMdd-HHmmss'))
$Backed = $false

function Do-Run([scriptblock]$Action, [string]$What) {
  if ($DryRun) { Write-Host "would: $What" } else { & $Action }
}

function Save-Backup([string]$Path, [string]$Name) {
  if (Test-Path $Path) {
    $dest = Join-Path $Backup $Name
    Do-Run { New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null; Copy-Item $Path $dest -Recurse -Force } "back up $Path"
    $script:Backed = $true
  }
}

foreach ($s in $Skills) { Save-Backup (Join-Path $Target "skills\$s") "skills\$s" }
foreach ($c in $Commands) { Save-Backup (Join-Path $Target "commands\$c") "commands\$c" }

if ($Uninstall) {
  foreach ($s in $Skills) { $p = Join-Path $Target "skills\$s"; if (Test-Path $p) { Do-Run { Remove-Item $p -Recurse -Force } "remove $p" } }
  foreach ($c in $Commands) { $p = Join-Path $Target "commands\$c"; if (Test-Path $p) { Do-Run { Remove-Item $p -Force } "remove $p" } }
  Write-Host "Removed the PRC suite from $Target."
} else {
  Do-Run { New-Item -ItemType Directory -Force (Join-Path $Target 'skills'), (Join-Path $Target 'commands') | Out-Null } "create $Target\skills and \commands"
  foreach ($s in $Skills) {
    $dest = Join-Path $Target "skills\$s"
    if (Test-Path $dest) { Do-Run { Remove-Item $dest -Recurse -Force } "remove old $dest" }
    Do-Run { Copy-Item (Join-Path $Src "skills\$s") $dest -Recurse } "copy skill $s"
  }
  foreach ($c in $Commands) { Do-Run { Copy-Item (Join-Path $Src "commands\$c") (Join-Path $Target "commands\$c") -Force } "copy command $c" }
  Write-Host "$(if ($DryRun) {(dry run) Would install} else {Installed}) the PRC suite into ${Target}:"
  Write-Host "  skill    $($Skills -join ', ')"
  Write-Host "  commands $(($Commands | ForEach-Object { '/' + ($_ -replace '\.md$','') }) -join ' ')"
  $settings = Join-Path $Home_ 'settings.json'
  if ((Test-Path $settings) -and (Select-String -Path $settings -Pattern '"prc@' -Quiet)) {
    Write-Warning "the prc plugin is also enabled; you'll see every command twice. Pick one: '/plugin uninstall prc@prc-skill' or '.\install.ps1 -Uninstall'."
  }
  Write-Host "Restart Claude Code (or start a new session) to load it."
}
if ($Backed) { Write-Host "Backup of what was there before: $Backup" }
