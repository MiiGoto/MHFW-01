FUNCTION_BLOCK FB_Cutter
VAR_INPUT
  Enable : BOOL;
  Boundary : BOOL;
  SealClose : BOOL;
END_VAR
VAR_OUTPUT
  Pulse : BOOL;
END_VAR
VAR
END_VAR
Pulse := Enable AND Boundary AND SealClose;
END_FUNCTION_BLOCK
