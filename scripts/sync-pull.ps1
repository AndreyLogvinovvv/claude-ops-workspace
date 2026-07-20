# Sync PULL: bring the latest copy from the NAS (claude-sync) to this PC.
# Run this BEFORE you start working on this PC.
# ASCII-only on purpose (PowerShell 5.1 misreads UTF-8-without-BOM .ps1).

$wsLocal  = "$env:USERPROFILE\MCP"                 # your workspace root
$memLocal = (Get-ChildItem "$env:USERPROFILE\.claude\projects" -Directory -Filter '*MCP*' -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName)
if ($memLocal) { $memLocal = Join-Path $memLocal 'memory' }
$notesLocal = "$env:USERPROFILE\local-notes"       # optional personal notes (NAS-only, never git)

# NAS root: drive letter differs between PCs, so probe candidates; UNC needs no mapping at all.
$nasRoot = $null
foreach ($cand in @('X:\claude-sync','Y:\claude-sync','\\YOUR-NAS\share\claude-sync')) {
    if (Test-Path $cand) { $nasRoot = $cand; break }
}
$wsNas    = "$nasRoot\workspace"
$memNas   = "$nasRoot\memory"
$notesNas = "$nasRoot\notes"

$xd = @('.git','.venv','node_modules','__pycache__','.pytest_cache','dist','build','__MACOSX')
$xf = @('*.pyc','*.log','.DS_Store','._*','.mcp.json')

if (-not $nasRoot) {
    Write-Host 'ERROR: NAS (claude-sync) is not reachable. Is the NAS online?' -ForegroundColor Red
    pause; exit 1
}
Write-Host ('NAS root: ' + $nasRoot) -ForegroundColor DarkGray
# Safety: refuse to pull if the NAS master looks empty/broken (would wipe local files).
if (-not (Test-Path (Join-Path $wsNas 'CLAUDE.md'))) {
    Write-Host "ERROR: NAS workspace looks empty (no CLAUDE.md at $wsNas). Aborting to protect your local files." -ForegroundColor Red
    pause; exit 1
}

if (Test-Path (Join-Path $nasRoot 'LAST-SYNC.txt')) {
    Write-Host ('Last synced: ' + (Get-Content (Join-Path $nasRoot 'LAST-SYNC.txt'))) -ForegroundColor Yellow
    Write-Host ''
}

Write-Host 'Pulling workspace from NAS...' -ForegroundColor Cyan
robocopy $wsNas $wsLocal /MIR /XD $xd /XF $xf /R:2 /W:2 /NFL /NDL /NP
if ($LASTEXITCODE -ge 8) { Write-Host "ERROR: workspace copy failed (robocopy $LASTEXITCODE)" -ForegroundColor Red; pause; exit 1 }

if ($memLocal) {
    Write-Host 'Pulling memory from NAS...' -ForegroundColor Cyan
    robocopy $memNas $memLocal /MIR /XF ._* .DS_Store /R:2 /W:2 /NFL /NDL /NP
    if ($LASTEXITCODE -ge 8) { Write-Host "ERROR: memory copy failed (robocopy $LASTEXITCODE)" -ForegroundColor Red; pause; exit 1 }
}

# Local notes (personal, NAS-only; never goes to git/Drive).
if (Test-Path $notesNas) {
    Write-Host 'Pulling local notes from NAS...' -ForegroundColor Cyan
    robocopy $notesNas $notesLocal /MIR /XF ._* .DS_Store /R:2 /W:2 /NFL /NDL /NP
    if ($LASTEXITCODE -ge 8) { Write-Host "ERROR: notes copy failed (robocopy $LASTEXITCODE)" -ForegroundColor Red; pause; exit 1 }
}

# Secrets: place gitignored key/token files from the NAS off-git folder onto this machine.
# Mirror of the block in sync-push.ps1 — one line per secret file.
$secNas = "$nasRoot\secrets"
$up = $env:USERPROFILE
if (Test-Path $secNas) {
    Write-Host 'Pulling secrets from NAS...' -ForegroundColor Cyan
    if (Test-Path "$secNas\MCP\.mcp.json") { robocopy "$secNas\MCP" "$up\MCP" .mcp.json /R:2 /W:2 /NFL /NDL /NP | Out-Null }
    # if (Test-Path "$secNas\MCP\my-project") { robocopy "$secNas\MCP\my-project" "$up\MCP\my-project" service_account.json token.json /R:2 /W:2 /NFL /NDL /NP | Out-Null }
}

Write-Host ''
Write-Host 'DONE. This PC now has the latest copy. You can start working.' -ForegroundColor Green
pause
