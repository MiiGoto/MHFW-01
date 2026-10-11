# Public repository provenance

Published 2026-10-11 with the project owner's explicit authorization.
This repository contains only MHFW-01, exported from local source commit
`3b89d3e`. The parent robotics repository, its history and unrelated projects
are retained locally and are not included here.

PLC, simulator, HMI and script bytes match the tested source commit.
`source_hashes.json` records their SHA-256 hashes. The recorded 24 native PLC
integration tests and 4 unit tests refer to the original Windows commissioning
run, not a fresh installation on another PC. User directory names in the copied
text logs were replaced with `<user>`; the original records remain local.

Beremiz/MatIEC/compiler binaries, generated DLL/C build output and generated
PLC keys are excluded. Setup downloads the official tools; their own licenses
apply. No third-party machine drawings or proprietary designs are included.
Fujikikai's public product information was used only for functional inspiration.
Hardware, thermal sealing, blade operation and certified safety remain HOLD.

No open-source license grant is specified for the independently authored project
files in this revision. Public visibility alone is not a license grant. The
third-party tools retain the licensing described in plc_environment.md.
