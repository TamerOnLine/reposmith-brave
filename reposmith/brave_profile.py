from __future__ import annotations
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Embedded PowerShell scripts and default configuration content
# ---------------------------------------------------------------------------

LAUNCH_BRAVE_PS1 = r'''
<#
.SYNOPSIS
  Launch Brave with project-defined ports and open related URLs.

.DESCRIPTION
  - Reads ports from .brave-ports.conf (one port per line).
  - If no file is found, defaults to ports 8000 and 5173.
  - Reads extra URLs from .brave-profile.conf (one URL per line).
  - Allows optional -Auto or -NoTabs flags.
#>

param(
  [string]$Name = "Brave (Project)",
  [string]$ProfileDir = ".brave-profile",
  [switch]$Auto,
  [switch]$NoTabs
)

# ---- Helpers ---------------------------------------------------------------

function Resolve-Brave {
  $paths = @(
    "$Env:LOCALAPPDATA\BraveSoftware\Brave-Browser\Application\brave.exe",
    "$Env:ProgramFiles\BraveSoftware\Brave-Browser\Application\brave.exe",
    "$Env:ProgramFiles(x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
  )
  foreach ($p in $paths) { if (Test-Path $p) { return $p } }
  throw "Brave not found."
}

function Read-Ports {
  $conf = Join-Path (Get-Location) ".brave-ports.conf"
  $ports = @()
  if (Test-Path $conf) {
    Get-Content $conf | ForEach-Object {
      $t = $_.Trim()
      if ($t -match '^\d+$') { $ports += [int]$t }
    }
  }
  if ($ports.Count -eq 0) { $ports = @(8000,5173) }
  return $ports
}

function Read-ExtraUrls {
  $conf = Join-Path (Get-Location) ".brave-profile.conf"
  $urls = @()
  if (Test-Path $conf) {
    Get-Content $conf | ForEach-Object {
      $u = $_.Trim()
      if ($u -and -not $u.StartsWith('#')) { $urls += $u }
    }
  }
  return $urls
}

# ---- Main ------------------------------------------------------------------

$brave = Resolve-Brave
$profilePath = Join-Path (Get-Location) $ProfileDir
New-Item -ItemType Directory -Force -Path $profilePath | Out-Null

$ports = Read-Ports
$urlsPorts = $ports | ForEach-Object { "http://localhost:$($_)" }
$urlsConf  = Read-ExtraUrls

if ($NoTabs) {
  $urlsToOpen = @()
}
elseif ($Auto) {
  $urlsToOpen = ($urlsPorts + $urlsConf) | Select-Object -Unique
}
else {
  Write-Host "Available URLs:" -ForegroundColor Cyan
  $combined = ($urlsPorts + $urlsConf) | Select-Object -Unique
  for ($i=0; $i -lt $combined.Count; $i++) {
    Write-Host "[$i] $($combined[$i])"
  }
  $choice = Read-Host "Enter comma-separated indices or press Enter for all"
  if ([string]::IsNullOrWhiteSpace($choice)) {
    $urlsToOpen = $combined
  } else {
    $indices = $choice -split '[,\s]+' | ForEach-Object { [int]$_ }
    $urlsToOpen = foreach ($ix in $indices) {
      if ($ix -ge 0 -and $ix -lt $combined.Count) { $combined[$ix] }
    }
  }
}

$argList = @("--user-data-dir=$profilePath")
foreach ($u in $urlsToOpen) { $argList += @("--new-tab", $u) }

Start-Process -FilePath $brave -ArgumentList $argList
Write-Host "Brave launched with profile: $profilePath" -ForegroundColor Green
if ($urlsToOpen.Count -gt 0) {
  Write-Host ("Opened tabs:`n - " + ($urlsToOpen -join "`n - "))
} else {
  Write-Host "No tabs opened (profile only). Add ports in .brave-ports.conf." -ForegroundColor Yellow
}
'''

MAKE_SHORTCUT_PS1 = r'''
param(
  [string]$Name = "Brave (Project)",
  [string]$ProfileDir = ".brave-profile"
)
$brave = "${env:ProgramFiles}\BraveSoftware\Brave-Browser\Application\brave.exe"
if (-not (Test-Path $brave)) {
  $brave = "${env:ProgramFiles(x86)}\BraveSoftware\Brave-Browser\Application\brave.exe"
}
if (-not (Test-Path $brave)) { Write-Error "Brave not found."; exit 1 }

$target = "`"$brave`" --user-data-dir=`"$PWD\$ProfileDir`""
$WScriptShell = New-Object -ComObject WScript.Shell
$Desktop = [Environment]::GetFolderPath("Desktop")
$Shortcut = $WScriptShell.CreateShortcut("$Desktop\$Name.lnk")
$Shortcut.TargetPath = $brave
$Shortcut.Arguments = "--user-data-dir=`"$PWD\$ProfileDir`""
$Shortcut.WorkingDirectory = "$PWD"
$Shortcut.Save()
Write-Host "Shortcut created on Desktop."
'''

CLEANUP_PS1 = r'''
param([string]$ProfileDir = ".brave-profile")
$path = Join-Path (Get-Location) $ProfileDir
if (Test-Path $path) {
  Remove-Item -Recurse -Force $path
  Write-Host "Removed $path"
} else {
  Write-Host "Nothing to remove at $path"
}
'''

DEFAULT_CONF = """# Lines starting with # are ignored.
# Add URLs to open automatically (one per line)
# http://localhost:8000
# http://localhost:5173
"""

DEFAULT_PORTS_CONF = """# Ports for this project (one per line)
8000
5173
"""

# ---------------------------------------------------------------------------
# Python functions
# ---------------------------------------------------------------------------

def init_brave_profile(root: Path) -> None:
    """Scaffold per-project Brave profile and tools."""
    root = Path(root)
    tools = root / "tools"
    tools.mkdir(parents=True, exist_ok=True)

    prof = root / ".brave-profile"
    prof.mkdir(exist_ok=True)

    (prof / "README.txt").write_text(
        "Per-project Brave profile.\nLaunch Brave with --user-data-dir pointing here.\n",
        encoding="utf-8",
    )

    (prof / "prefs.json").write_text(
        json.dumps({"homepage": "about:blank", "first_run_tabs": []}, indent=2),
        encoding="utf-8",
    )

    (root / ".brave-profile.conf").write_text(DEFAULT_CONF, encoding="utf-8")
    (root / ".brave-ports.conf").write_text(DEFAULT_PORTS_CONF, encoding="utf-8")

    (tools / "launch_brave.ps1").write_text(LAUNCH_BRAVE_PS1.lstrip(), encoding="utf-8")
    (tools / "make_brave_shortcut.ps1").write_text(MAKE_SHORTCUT_PS1.lstrip(), encoding="utf-8")
    (tools / "cleanup_brave_profile.ps1").write_text(CLEANUP_PS1.lstrip(), encoding="utf-8")

def add_vscode_task(root: Path) -> None:
    """Append Brave launch tasks to VS Code tasks.json."""
    vscode = root / ".vscode"
    vscode.mkdir(exist_ok=True)
    tasks = vscode / "tasks.json"

    task_obj = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Brave: Launch project profile",
                "type": "shell",
                "command": "pwsh",
                "args": ["-File", "${workspaceFolder}/tools/launch_brave.ps1"],
                "problemMatcher": [],
            },
            {
                "label": "Brave: Launch (Auto)",
                "type": "shell",
                "command": "pwsh",
                "args": ["-File", "${workspaceFolder}/tools/launch_brave.ps1", "-Auto"],
                "problemMatcher": [],
            },
            {
                "label": "Brave: Launch (No Tabs)",
                "type": "shell",
                "command": "pwsh",
                "args": ["-File", "${workspaceFolder}/tools/launch_brave.ps1", "-NoTabs"],
                "problemMatcher": [],
            },
        ],
    }

    if tasks.exists():
        try:
            existing = json.loads(tasks.read_text(encoding="utf-8"))
            if isinstance(existing, dict):
                ex_tasks = existing.setdefault("tasks", [])
                existing_labels = {t.get("label") for t in ex_tasks if isinstance(t, dict)}
                for t in task_obj["tasks"]:
                    if t["label"] not in existing_labels:
                        ex_tasks.append(t)
                tasks.write_text(json.dumps(existing, indent=2), encoding="utf-8")
                return
        except Exception:
            pass

    tasks.write_text(json.dumps(task_obj, indent=2), encoding="utf-8")

def setup_brave(root: Path) -> None:
    """Set up Brave integration."""
    init_brave_profile(root)
    add_vscode_task(root)

__all__ = ["setup_brave", "init_brave_profile", "add_vscode_task"]
