# Motion model

Axis 1 infeed, 2 film, 3 center seal, 4 end jaws, 5 discharge.
Position/target/actual/error in mm; velocity mm/s; acceleration mm/s².
Center rollers use equivalent surface travel rather than angular inertia.
End-seal axis is jaw opening (0 closed, 40 open), not a manufacturer rotary-servo design.
The simulated following model caps requested velocity and acceleration, then clamps an
overshooting step to its target. That endpoint clamp can produce a larger reported deceleration
than the requested limit, especially on the jaw axis; it is an ideal kinematic constraint,
not a validated drive/torque/inertia model. Fault freezes also stop velocity instantly.

Linear speed = bag pitch × packaging rate / 60. Initial 120 mm × 10/min gives 20 mm/s.
Bag phase = fractional(actual film position + offset)/pitch.
Seal phase = bag phase + phase offset, wrapped to [0,1).
Cam: closed dwell within 0.04 cycle of a boundary, linear opening ramp to 40 mm by 0.20;
open through the product crossing. This differs from equal-speed axis rotation.
Recipe limits constrain film offset to ±5 mm and seal offset to ±0.03 cycle.
Following error >8 mm, or film target/actual difference >8 mm, stops the PLC.
Startup jaw following transient has a 0.6 simulated-second persistence filter in the sensor model.

No encoder calibration, thermal dwell validation, force control or real drive integration is claimed.
