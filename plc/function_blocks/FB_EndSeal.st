FUNCTION_BLOCK FB_EndSeal
VAR_INPUT
  Enable : BOOL;
  CamClose : BOOL;
  CamTarget : REAL;
END_VAR
VAR_OUTPUT
  Close : BOOL;
  Target : REAL;
END_VAR
VAR
END_VAR
Close := Enable AND CamClose;
IF Enable THEN Target := CamTarget; ELSE Target := 40.0; END_IF;
END_FUNCTION_BLOCK
