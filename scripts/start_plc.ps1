. "$PSScriptRoot/environment.ps1"
& $mhfwPython -X utf8 $mhfwCLI --project-home "$mhfwAscii/plc/beremiz" -e $mhfwExtension --keep transfer run 2>&1 | Tee-Object "$mhfwProject/logs/runtime.txt"
if ($LASTEXITCODE) { throw 'PLC runtime failed. See logs/runtime.txt' }
