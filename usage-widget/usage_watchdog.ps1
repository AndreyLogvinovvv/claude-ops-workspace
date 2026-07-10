# Keeps the usage server alive: restarts it if nothing is listening on port 3999.
while ($true) {
    $port = Get-NetTCPConnection -LocalPort 3999 -EA SilentlyContinue
    if (-not $port) {
        Start-Process pythonw -ArgumentList (Join-Path $PSScriptRoot 'usage_server.py') -WindowStyle Hidden
    }
    Start-Sleep -Seconds 10
}
