. "$PSScriptRoot/setup_paths.ps1"
$mhfwTools=Join-Path $mhfwProject 'tools'
New-Item -ItemType Directory -Force $mhfwTools | Out-Null
$mhfwFiles=@{
 'beremiz.zip'='https://github.com/beremiz/beremiz/releases/download/v1.6.0/beremiz-windows-portable_1.6.0_amd64.zip'
 'beremiz151.zip'='https://github.com/beremiz/beremiz/releases/download/v1.5.1/beremiz-windows-portable_1.5.1_amd64.zip'
 'beremiz-1.5.1-source.zip'='https://github.com/beremiz/beremiz/archive/refs/tags/v1.5.1.zip'
}
foreach ($mhfwName in $mhfwFiles.Keys) {
    $mhfwDest=Join-Path $mhfwTools $mhfwName
    if (-not (Test-Path -LiteralPath $mhfwDest)) { Invoke-WebRequest $mhfwFiles[$mhfwName] -OutFile $mhfwDest }
}
$mhfwPython=Join-Path $mhfwTools 'beremiz/msys64/ucrt64/bin/python.exe'
if (-not (Test-Path -LiteralPath $mhfwPython)) {
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory((Join-Path $mhfwTools 'beremiz.zip'),(Join-Path $mhfwTools 'beremiz'))
}
& $mhfwPython -X utf8 "$PSScriptRoot/extract_tools.py"
if ($LASTEXITCODE) { throw 'Tool extraction failed' }
Write-Host 'Portable toolchain ready. Run scripts/build_plc.ps1.'
