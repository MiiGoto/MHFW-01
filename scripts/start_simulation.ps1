param([switch]$Accelerated)
. "$PSScriptRoot/environment.ps1"
$mhfwArgs = @('-X','utf8',"$mhfwAscii/hmi/backend/server.py")
if ($Accelerated) { $mhfwArgs += '--accelerated' }
& $mhfwPython @mhfwArgs
