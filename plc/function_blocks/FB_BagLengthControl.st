FUNCTION_BLOCK FB_BagLengthControl
VAR_INPUT
  Position : REAL;
  Pitch : REAL;
  Offset : REAL;
  Reset : BOOL;
END_VAR
VAR_OUTPUT
  Phase : REAL;
  Boundary : BOOL;
END_VAR
VAR
  Previous : REAL;
  Turns : REAL;
END_VAR
Turns := (Position + Offset) / Pitch;
Phase := Turns - DINT_TO_REAL(TRUNC(Turns));
IF Phase < 0.0 THEN Phase := Phase + 1.0; END_IF;
Boundary := (Phase < Previous) AND NOT Reset;
Previous := Phase;
END_FUNCTION_BLOCK
