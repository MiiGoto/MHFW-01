FUNCTION_BLOCK FB_AxisSynchronization
VAR_INPUT
  Phase : REAL;
  Offset : REAL;
END_VAR
VAR_OUTPUT
  SealPhase : REAL;
  JawTarget : REAL;
  Close : BOOL;
END_VAR
VAR
  Distance : REAL;
END_VAR
SealPhase := Phase + Offset;
SealPhase := SealPhase - DINT_TO_REAL(TRUNC(SealPhase));
IF SealPhase < 0.0 THEN SealPhase := SealPhase + 1.0; END_IF;
Distance := MIN(SealPhase, 1.0 - SealPhase);
(* Electronic cam: closed dwell +/-0.04, ramp to fully open at 0.20. *)
JawTarget := LIMIT(0.0, (Distance - 0.04) * 250.0, 40.0);
Close := Distance < 0.04;
END_FUNCTION_BLOCK
