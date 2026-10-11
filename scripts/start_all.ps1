param([switch]$Accelerated)
. "$PSScriptRoot/environment.ps1"
if (Test-Path "$mhfwProject/logs/processes.json") { throw 'Run stop_all.ps1 before starting another session.' }
& "$PSScriptRoot/build_plc.ps1"
$mhfwShell=(Get-Process -Id $PID).Path
$mhfwPlc=Start-Process -FilePath $mhfwShell -ArgumentList @('-NoProfile','-File',('"'+$PSScriptRoot+'/start_plc.ps1"')) -WorkingDirectory $mhfwProject -WindowStyle Hidden -PassThru
$mhfwHmiArgs=@('-NoProfile','-File',('"'+$PSScriptRoot+'/start_simulation.ps1"'))
if ($Accelerated) { $mhfwHmiArgs+='-Accelerated' }
$mhfwHmi=Start-Process -FilePath $mhfwShell -ArgumentList $mhfwHmiArgs -WorkingDirectory $mhfwProject -WindowStyle Hidden -PassThru -RedirectStandardOutput "$mhfwProject/logs/hmi_console.txt" -RedirectStandardError "$mhfwProject/logs/hmi_error.txt"
@{
 plc=@{id=$mhfwPlc.Id;started=$mhfwPlc.StartTime.ToUniversalTime().ToString('o');path=$mhfwShell}
 hmi=@{id=$mhfwHmi.Id;started=$mhfwHmi.StartTime.ToUniversalTime().ToString('o');path=$mhfwShell}
} | ConvertTo-Json | Set-Content "$mhfwProject/logs/processes.json"
Write-Host 'HMI: http://127.0.0.1:8080  (allow a few seconds for PLC transfer)'
Write-Host 'Stop: scripts/stop_all.ps1'
