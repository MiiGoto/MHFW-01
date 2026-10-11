$ErrorActionPreference = 'Stop'
$mhfwProject = Split-Path -Parent $PSScriptRoot
$mhfwTempRoot = Join-Path $env:TEMP 'mhfw-reva'
New-Item -ItemType Directory -Force -Path $mhfwTempRoot | Out-Null
$mhfwAscii = Join-Path $mhfwTempRoot 'project'
if (-not (Test-Path -LiteralPath $mhfwAscii)) {
    New-Item -ItemType Junction -Path $mhfwAscii -Target $mhfwProject | Out-Null
}
if ((Get-Item -LiteralPath $mhfwAscii).Target -ne $mhfwProject) {
    throw "Existing temporary junction points to another project: $mhfwAscii"
}
$env:MHFW_ASCII_ROOT = $mhfwAscii
$env:PYTHONUTF8 = '1'
$mhfwPython = Join-Path $mhfwAscii 'tools/beremiz/msys64/ucrt64/bin/python.exe'
$mhfwCLI = Join-Path $mhfwAscii 'tools/beremiz-1.5.1/Beremiz_cli.py'
$mhfwExtension = Join-Path $mhfwAscii 'scripts/beremiz_paths.py'
if (-not (Test-Path -LiteralPath $mhfwPython)) { throw 'Run scripts/setup.ps1 first.' }
New-Item -ItemType Directory -Force (Join-Path $mhfwProject 'logs') | Out-Null
