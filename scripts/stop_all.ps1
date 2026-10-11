. "$PSScriptRoot/environment.ps1"
try { Invoke-RestMethod -Uri 'http://127.0.0.1:8080/api/command' -Method Post -ContentType 'application/json' -Body '{"action":"stop"}' -TimeoutSec 2 | Out-Null } catch { Write-Host 'HMI already stopped/unavailable.' }
Start-Sleep -Milliseconds 200
$mhfwPidFile="$mhfwProject/logs/processes.json"
if (Test-Path -LiteralPath $mhfwPidFile) {
    $mhfwIds=Get-Content -LiteralPath $mhfwPidFile -Raw | ConvertFrom-Json
    # Only process trees created by start_all; no global python/process termination.
    foreach ($mhfwEntry in @($mhfwIds.plc,$mhfwIds.hmi)) {
        $mhfwId=$mhfwEntry.id
        $mhfwProc=Get-Process -Id $mhfwId -ErrorAction SilentlyContinue
        if ($mhfwProc) {
            if ($mhfwProc.Path -ne $mhfwEntry.path -or $mhfwProc.StartTime.ToUniversalTime().Ticks -ne ([datetime]$mhfwEntry.started).ToUniversalTime().Ticks) { throw 'PID was reused; refusing termination.' }
            & taskkill.exe /PID $mhfwId /T /F | Out-Null
            if ($LASTEXITCODE) { throw 'Could not stop owned process tree. Keep processes.json and retry in the same Windows user session.' }
        }
    }
    Remove-Item -LiteralPath $mhfwPidFile
}
