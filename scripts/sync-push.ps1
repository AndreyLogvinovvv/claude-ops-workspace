# Sync PUSH: send local workspace + Claude memory to the NAS (claude-sync).
# Run this WHEN YOU FINISH working on this PC.
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

# Junk / per-machine stuff that must NOT travel over the NAS.
$xd = @('.git','.venv','node_modules','__pycache__','.pytest_cache','dist','build','__MACOSX')
$xf = @('*.pyc','*.log','.DS_Store','._*','.mcp.json')

if (-not $nasRoot) {
    Write-Host 'ERROR: NAS (claude-sync) is not reachable. Is the NAS online?' -ForegroundColor Red
    pause; exit 1
}
Write-Host ('NAS root: ' + $nasRoot) -ForegroundColor DarkGray
# Safety: refuse to push an empty/broken local workspace (would wipe the NAS master).
if (-not (Test-Path (Join-Path $wsLocal 'CLAUDE.md'))) {
    Write-Host "ERROR: local workspace looks empty (no CLAUDE.md at $wsLocal). Aborting to protect the NAS copy." -ForegroundColor Red
    pause; exit 1
}

Write-Host 'Pushing workspace to NAS...' -ForegroundColor Cyan
robocopy $wsLocal $wsNas /MIR /XD $xd /XF $xf /R:2 /W:2 /NFL /NDL /NP
if ($LASTEXITCODE -ge 8) { Write-Host "ERROR: workspace copy failed (robocopy $LASTEXITCODE)" -ForegroundColor Red; pause; exit 1 }

if ($memLocal -and (Test-Path $memLocal)) {
    Write-Host 'Pushing memory to NAS...' -ForegroundColor Cyan
    robocopy $memLocal $memNas /MIR /XF ._* .DS_Store /R:2 /W:2 /NFL /NDL /NP
    if ($LASTEXITCODE -ge 8) { Write-Host "ERROR: memory copy failed (robocopy $LASTEXITCODE)" -ForegroundColor Red; pause; exit 1 }
}

# Local notes (personal, NAS-only; never goes to git/Drive).
if (Test-Path $notesLocal) {
    Write-Host 'Pushing local notes to NAS...' -ForegroundColor Cyan
    robocopy $notesLocal $notesNas /MIR /XF ._* .DS_Store /R:2 /W:2 /NFL /NDL /NP
    if ($LASTEXITCODE -ge 8) { Write-Host "ERROR: notes copy failed (robocopy $LASTEXITCODE)" -ForegroundColor Red; pause; exit 1 }
}

# Secrets: specific gitignored key/token files -> NAS off-git folder (NEVER in workspace git).
# Add one robocopy line per secret file your projects need, e.g.:
$secNas = "$nasRoot\secrets"
$up = $env:USERPROFILE
Write-Host 'Pushing secrets to NAS (off-git folder)...' -ForegroundColor Cyan
if (Test-Path "$up\MCP\.mcp.json") { robocopy "$up\MCP" "$secNas\MCP" .mcp.json /R:2 /W:2 /NFL /NDL /NP | Out-Null }
# if (Test-Path "$up\MCP\my-project") { robocopy "$up\MCP\my-project" "$secNas\MCP\my-project" service_account.json token.json /R:2 /W:2 /NFL /NDL /NP | Out-Null }

"$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  pushed from $env:COMPUTERNAME" | Set-Content (Join-Path $nasRoot 'LAST-SYNC.txt') -Encoding UTF8

Write-Host ''
Write-Host 'DONE. The latest copy is now on the NAS. You can switch to another PC.' -ForegroundColor Green
pause
