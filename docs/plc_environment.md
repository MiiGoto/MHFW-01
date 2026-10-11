# PLC environment

Use the official Beremiz 1.5.1 IDE/CLI and runtime source, its matching MatIEC compiler,
and Python/GCC distributed in the official Beremiz 1.6.0 portable package.
These are project-local, free tools. No administrator installation is required.
Exact archives and SHA-256 hashes are recorded in toolchain_hashes.json.

The 1.6.0 native Win32 build attempted here failed because its split-runtime generator
included dlfcn.h. Rev A therefore uses the existing 1.5.1 monolithic DLL runtime.
The newer MatIEC cannot be mixed with 1.5.1: it no longer produced VARIABLES.csv in this build.
Use the 1.5.1 compiler, not the 1.6.0 one.

Japanese path support in this MinGW setup requires an ASCII temporary junction plus explicit
GCC_EXEC_PREFIX and MATIEC_PATH. environment.ps1 creates the junction after checking its target;
beremiz_paths.py configures tool paths inside the Beremiz process. Python uses UTF-8 mode.
No global PATH, registry, firewall, execution policy or WSL setting is modified.

Sources:
- https://beremiz.org/download
- https://github.com/beremiz/beremiz/releases/tag/v1.5.1
- https://github.com/beremiz/beremiz/releases/tag/v1.6.0
- https://beremiz.org/getting-started

Beremiz IDE is GPL, reference runtime LGPL, MatIEC GPL; bundled tools retain their licenses.
Third-party tools/archives are ignored by Git. The project sources are independently authored.
CODESYS simulation is not a dependency and was not installed or validated.
