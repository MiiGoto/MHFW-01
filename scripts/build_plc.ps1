. "$PSScriptRoot/environment.ps1"
& $mhfwPython -X utf8 "$mhfwAscii/scripts/generate_plc.py"
if ($LASTEXITCODE) { throw 'PLCopen generation failed' }
& $mhfwPython -X utf8 $mhfwCLI --project-home "$mhfwAscii/plc/beremiz" -e $mhfwExtension build 2>&1 | Tee-Object "$mhfwProject/logs/build.txt"
if ($LASTEXITCODE) { throw 'PLC build failed. See logs/build.txt' }
