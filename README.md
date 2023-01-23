[![GitIgnore](../../actions/workflows/GitIgnore.yml/badge.svg)](../../actions/workflows/GitIgnore.yml)

# Industrial Brainframe - Device library

## TODO

### Generic repo / project wide

1. Add build action
1. Add automatic tests

### Must have

1. `Fb_DevAxis`:
	- Fb_DevAxis.Init VAR_INPUT default values have no effect (move defaults to Fb_DevAxis VARs or use PROPERTY)
	- Add feature: check if online motor parameters match project parameters
	- When STO is not OK, no fault/error is generated; this is as designed (handled by higher level safety system), but is not very intuitive
	- Axis fault is only active for 1 PLC cycle
	- Entering manual mode before system has enabled gives Halt errors
	- Homing in manual mode should reset the Homed bit, but system still thinks drive is homed
	- Homing stays active even after CmdHold is no longer called
	- ExecWriteParameter is disabled (excluded from build), possible residue from added Delta servo
	- Delta bReverseHomingDirection BOOL is tie wrapped/duct taped in the lib, needs to be cleaned up
	- McReadSysVelo etc return an Error bool, this is not used in FB_DevAxis
	- Axes are NOT reset with a cold-reset, its state can therefore break tests (e.g., still busy with a command when test commences). Should the PLC program always reset axes after boot?
1. DevDigitalOut doesn't have a manual control screen; DevLight does have one and overlaps with DevDigitalOut -> derive DevLight from DevDigitalOut
1. Manual mode: when teaching, value is immediately set as Active parameter value. Is this expected behavior?

### Nice to have

1. Many CONCAT operations do not add a space, leading to ugly strings (e.g. "MotorEnable fault" instead of "Motor: Enable fault")
1. Add axis fault descriptions based on error codes (see https://infosys.beckhoff.com/content/1033/tc3ncerrcode/513151243.html)