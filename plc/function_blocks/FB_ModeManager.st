FUNCTION_BLOCK FB_ModeManager
VAR_INPUT
  StartPB : BOOL;
  StopPB : BOOL;
  Requested : INT;
  Alarm : INT;
  SingleDone : BOOL;
  Cold : BOOL;
END_VAR
VAR_OUTPUT
  Running : BOOL;
  Mode : INT;
END_VAR
VAR
  PrevStart : BOOL;
END_VAR
IF Cold THEN Running := FALSE; Mode := 4; END_IF;
IF Alarm = 0 AND Mode = 5 THEN Mode := 4; END_IF;
IF StartPB AND NOT PrevStart AND Alarm = 0 AND Requested >= 1 AND Requested <= 3 THEN Running := TRUE; Mode := Requested; END_IF;
IF StopPB OR SingleDone THEN Running := FALSE; Mode := 4; END_IF;
IF Alarm <> 0 THEN Running := FALSE; Mode := 5; END_IF;
PrevStart := StartPB;
END_FUNCTION_BLOCK
