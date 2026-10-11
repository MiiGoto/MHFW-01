# Control sequence

On startup the virtual batch sends a commissioning cold-reset while stopped.
Valid recipe and healthy guards/film/position/communication are required.
START rising edge selects requested MANUAL/AUTO/SINGLE. STOP has priority and enters PAUSE.
Continuous infeed/film/center/discharge targets advance only on fresh input transactions.
Film actual position determines bag phase. Electronic cam drives end jaws; a phase wrap with
closed jaw command requests cutting. The machine acknowledges one correctly positioned
product only if its modeled jaw gap is closed and the seal boundary is free of product.
ST counts acknowledged packages and rejected cuts. SINGLE pauses at the next bag boundary.

Alarm is latched. Clearing the cause does not restart or clear the alarm. Manual RESET with
healthy inputs clears it; a new START rising edge is required. Product-absence recovery
requires an observed product. Film end, double feed, axis error, jam, open guard, E-stop and
communication age >500 ms inhibit operation.

Alarm codes: 1 absent/stuck-off product, 2 stuck-on sensor, 3 double feed,
4 film end, 5 film position/slip, 6 seal zone product, 7 following error,
8 jam, 9 simulated guard/E-stop, 10 communication timeout, 11 invalid recipe.
Multiple simultaneous causes use the last applicable priority in the main ST source.
