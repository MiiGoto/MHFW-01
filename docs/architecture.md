# Architecture

Browser HMI → HTTP console (127.0.0.1:8080) → command queue → virtual I/O inputs
→ native Beremiz PLC scan (20 ms) → ST output targets/enables → UDP reply
→ Python five-axis model → product tracking/sensors → next scan.

The transport adapter contains no mode, sequence, alarm or motion control decisions.
It validates a binary frame, updates IEC globals before the scan, and publishes globals after it.
PLC and Python run in separate processes; Python never evaluates or interprets ST.
Screen drawing uses requestAnimationFrame; HMI state polls at 100 ms.
Machine steps are 20 ms, or 200 ms in accelerated mode, once per successful I/O transaction.
The actual PLC task remains 20 ms. Acceleration affects virtual elapsed time, not watchdog time.
There is no real-time or safety guarantee on Windows. The model freezes on communication loss.
