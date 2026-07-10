# Daily auto-backup: commit + push a working folder to its git remote.
# Intended to run on a schedule (e.g. Windows Task Scheduler).
#
# Auth: this script does NOT store any token. Configure git credentials once so
# pushes are non-interactive, e.g. Git Credential Manager / OS credential store.
#
# ASCII-only on purpose: PowerShell 5.1 misreads UTF-8-without-BOM .ps1 files,
# which breaks parsing if the file contains non-ASCII characters.

param(
    # Path to the git working tree to back up. Defaults to this repo's root.
    [string]$Repo   = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path,
    [string]$Branch = 'main'
)

$log = Join-Path $PSScriptRoot 'auto-backup.log'
function Log($m) {
    Add-Content -LiteralPath $log -Value ("{0}  {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $m) -Encoding UTF8
}

# Non-interactive: fail instead of prompting if credentials are missing.
$env:GIT_TERMINAL_PROMPT = '0'
$env:GCM_INTERACTIVE     = 'never'

& git -C $Repo add -A 2>$null

$changes = & git -C $Repo status --porcelain
if (-not $changes) { Log 'no changes - nothing to commit'; exit 0 }

$msg = 'chore: daily backup ' + (Get-Date -Format 'yyyy-MM-dd HH:mm')
& git -C $Repo commit -q -m $msg 2>$null
if ($LASTEXITCODE -ne 0) { Log "ERROR commit (code $LASTEXITCODE)"; exit 1 }

$pushOut = & git -C $Repo push origin $Branch 2>&1
if ($LASTEXITCODE -ne 0) { Log ("ERROR push (code $LASTEXITCODE): " + ($pushOut -join ' ')); exit 1 }

Log ("OK: " + $msg)
