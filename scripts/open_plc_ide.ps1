. "$PSScriptRoot/environment.ps1"
# Explicit interactive IDE request: run this script to edit/debug PLCopen project.
& $mhfwPython -X utf8 "$mhfwAscii/tools/beremiz-1.5.1/Beremiz.py" -e $mhfwExtension "$mhfwAscii/plc/beremiz"
