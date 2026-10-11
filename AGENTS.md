# MHFW-01 development rules

- Preserve the parent repository and unrelated changes. Stage only MHFW-01.
- Budget zero: no purchases, physical outputs, heater power, blades or motors.
- PLC decisions belong in IEC 61131-3 ST, executed by Beremiz/MatIEC native code.
- Python owns the machine model and transport, never a substitute PLC controller.
- Build with scripts/build_plc.ps1. Run native integration tests with exclusive PLC I/O ownership.
- Document actual test evidence and acceptance HOLDs. Software stop is not certified safety.
- No public repository creation or next development phase without a user request.
