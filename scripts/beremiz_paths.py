"""Beremiz extension: explicit portable toolchain paths, no global settings."""
import os
from pathlib import Path
# MHFW_ASCII_ROOT is a project junction created by environment.ps1.
mhfw_root=Path(os.environ['MHFW_ASCII_ROOT'])
mhfw_tools=mhfw_root/'tools/beremiz'
os.environ['PATH']=str(mhfw_tools/'msys64/ucrt64/bin')+os.pathsep+os.environ['PATH']
os.environ['MATIEC_PATH']=str(mhfw_root/'tools/beremiz151/matiec')
os.environ['GCC_EXEC_PREFIX']=str(mhfw_tools/'msys64/ucrt64/lib/gcc').replace('\\','/')+'/'
os.environ['MSYSTEM']='UCRT64'
os.environ['PYTHONUTF8']='1'
