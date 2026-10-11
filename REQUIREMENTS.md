# Requirements and traceability

| Requirement | Implementation / evidence |
|---|---|
| A PLC builds | 11 FB ST sources, PRG_PackagingMachine, PLCopen XML, logs/build.txt |
| B native runtime | Beremiz 1.5.1 LOCAL runtime, logs/runtime.txt |
| C Python machine | simulation/machine/model.py, five axis models |
| D actual I/O link | c_ext UDP request/reply, integration.py |
| E moving products | browser canvas animation, HMI state samples / screenshot |
| F PLC commands | ST-generated targets and enable signals, native integration |
| G HMI start/stop | /api/command and browser controls |
| H counts | physical model package acknowledgement counted in ST, JSONL log |
| I injected stop | native integration fault tests |
| J automated tests | scripts/run_tests.ps1, separate unit/integration logs |

Modes: MANUAL (continuous virtual jog), AUTO, SINGLE_CYCLE, PAUSE, FAULT.
Recipe editing is allowed only while stopped and reinitializes the virtual batch.
Simulation E-stop and guard signals are functional inputs; they are not safety-certified.
Virtual I/O is loopback-only, with no connection to physical equipment.
