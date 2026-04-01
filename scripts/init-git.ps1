# Run from project root:  powershell -ExecutionPolicy Bypass -File scripts/init-git.ps1
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root

$git = $null
foreach ($p in @(
    "C:\Program Files\Git\bin\git.exe",
    "C:\Program Files\Git\cmd\git.exe",
    "$env:LOCALAPPDATA\Programs\Git\bin\git.exe",
    "C:\Program Files (x86)\Git\bin\git.exe"
)) {
    if (Test-Path $p) { $git = $p; break }
}
if (-not $git) {
    $cmd = Get-Command git -ErrorAction SilentlyContinue
    if ($cmd) { $git = $cmd.Source }
}
if (-not $git) {
    Write-Host "Git not found. Install from https://git-scm.com/download/win and reopen the terminal." -ForegroundColor Red
    exit 1
}

Write-Host "Using: $git"
& $git --version

if (Test-Path ".git") {
    Write-Host "Repository already exists (.git present)." -ForegroundColor Yellow
} else {
    & $git init
}

& $git add -A
& $git status

$msg = "Initial commit: AI Internal Productivity Suite"
try {
    & $git commit -m $msg
    Write-Host "Done: $msg" -ForegroundColor Green
} catch {
    Write-Host "Nothing to commit or commit failed (see message above)." -ForegroundColor Yellow
}
