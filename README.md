[![GitIgnore](../../actions/workflows/GitIgnore.yml/badge.svg)](../../actions/workflows/GitIgnore.yml)

# Industrial Brainframe - Device library

## TODO

### Generic repo / project wide

1. Add build action
1. Add automatic tests

### Improvements

1. `Fb_DevAxis`:
	- Fb_DevAxis.Init VAR_INPUT default values have no effect (move defaults to Fb_DevAxis VARs or use PROPERTY)
	- Add feature: check if online motor parameters match project parameters
	- When STO is not OK, no fault/error is generated; this is as designed (handled by higher level safety system), but is not very intuitive


