FUNCTION_BLOCK FB_CenterSeal
VAR_INPUT
  Enable : BOOL;
  Fresh : BOOL;
  Reset : BOOL;
  Speed : REAL;
  StepSeconds : REAL;
END_VAR
VAR_OUTPUT
  Run : BOOL;
  Target : REAL;
END_VAR
VAR
END_VAR
IF Reset THEN Target := 0.0; END_IF;
Run := Enable;
IF Enable AND Fresh THEN Target := Target + Speed * StepSeconds; END_IF;
END_FUNCTION_BLOCK
