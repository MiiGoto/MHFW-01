. "$PSScriptRoot/environment.ps1"
Push-Location $mhfwProject
try {
    & $mhfwPython -X utf8 -m unittest discover -s simulation/tests -v 2>&1 | Tee-Object logs/unit_tests.txt
    if ($LASTEXITCODE) { throw 'Machine unit tests failed' }
    & $mhfwPython -X utf8 plc/tests/integration.py 2>&1 | Tee-Object logs/integration_tests.txt
    if ($LASTEXITCODE) { throw 'Native PLC integration tests failed' }
} finally { Pop-Location }
