FUNCTION_BLOCK FB_ProductDetection
VAR_INPUT
  Present : BOOL;
  Run : BOOL;
  Fresh : BOOL;
  StepSeconds : REAL;
  Period : REAL;
  Reset : BOOL;
END_VAR
VAR_OUTPUT
  Missing : BOOL;
  StuckOn : BOOL;
END_VAR
VAR
  AbsentTime : REAL;
  PresentTime : REAL;
END_VAR
IF Reset OR NOT Run THEN AbsentTime := 0.0; PresentTime := 0.0; END_IF;
IF Run AND Fresh THEN
 IF Present THEN AbsentTime := 0.0; PresentTime := PresentTime + StepSeconds;
 ELSE PresentTime := 0.0; AbsentTime := AbsentTime + StepSeconds; END_IF;
END_IF;
Missing := AbsentTime > 2.2 * Period;
StuckOn := PresentTime > 1.2 * Period;
END_FUNCTION_BLOCK
