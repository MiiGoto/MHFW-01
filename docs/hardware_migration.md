# Future hardware migration — no purchases or physical commissioning in Rev A

Maintain recipe, mode, status and axis interface semantics. Replace virtual sensors/actuators
through a physical I/O adapter only after independent safety and mechanical design reviews.

| Candidate | Design implication |
|---|---|
| PLC + STM32 | IEC supervisor plus microcontroller drive/encoder loops; define heartbeat and safe output defaults |
| STM32 controller | Requires a separately validated IEC runtime or explicit rewritten firmware; the PC runtime is not firmware |
| Stepper | Candidate for low-speed film/infeed; missed steps require encoder or independent position checks |
| BLDC | Candidate for smoother continuous drives; requires commutation, feedback and drive qualification |
| Encoder | Supplies actual position and phase; resolution, latency and missing-signal response must be tested |

These are conceptual tradeoffs, not component selections or verified hardware compatibility.
Before heaters, blades, motors or food contact: electrical and machinery risk assessment,
independent stop circuit/guarding, thermal runaway cutoff, hygienic materials and cleanability,
film seal process qualification, and food-contact/regulatory assessment appropriate to use.
No physical safety standard compliance is established by this simulation.
