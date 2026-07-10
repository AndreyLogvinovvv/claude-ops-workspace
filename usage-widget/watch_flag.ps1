# Optional helper: watches for a refresh flag next to this script and prints it.
# The flag file is created by usage_server.py on /trigger.
$flag = Join-Path $PSScriptRoot 'refresh_flag.txt'
while ($true) {
    if (Test-Path $flag) {
        $t = Get-Content $flag -Raw
        Write-Output "REFRESH:$t"
        Remove-Item $flag -Force
    }
    Start-Sleep -Milliseconds 500
}
