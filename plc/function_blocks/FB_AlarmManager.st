FUNCTION_BLOCK FB_AlarmManager
VAR_INPUT
  Cause : INT;
  ResetPB : BOOL;
  RecoveryOK : BOOL;
  Cold : BOOL;
END_VAR
VAR_OUTPUT
  Alarm : INT;
END_VAR
VAR
  PrevReset : BOOL;
END_VAR
IF Cold THEN Alarm := 0; END_IF;
IF ResetPB AND NOT PrevReset AND RecoveryOK THEN Alarm := 0; END_IF;
IF Cause <> 0 THEN Alarm := Cause; END_IF;
PrevReset := ResetPB;
END_FUNCTION_BLOCK
