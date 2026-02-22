# OctoPrint + Prusa XL Known Quirks

Known behaviors when using OctoPrint with a Prusa XL. See [OctoPrint-PrusaXL](https://github.com/mlbreit/octoprint-prusaxl) for profiles and setup.

## Absorbing Heat (5–8 Minute Pause)

**Symptom:** After homing and bed mesh calibration, the printer appears stuck for 5–8 minutes with no status change in OctoPrint.

**Cause:** The Prusa XL has a built-in "absorbing heat" phase. The printer is heating the chamber/bed to stabilize before printing. This is normal and expected.

**What to do:** Wait. The printer will start printing after the same duration you would see if printing from USB. There is no visible "Absorbing Heat" message in OctoPrint or on the XL screen during this phase.

## Object Too Big Warning

**Symptom:** OctoPrint shows a warning that the object(s) are too big for the build area when starting a print.

**Cause:** False positive. The Prusa XL build volume is 360×360×360 mm.

**What to do:** If you are confident the model fits within 360×360×360 mm, click Print again. The warning often clears on retry.

## PrusaSlicer and G-code

**Recommendation:** Disable Prusa's bgcode generation for projects you will print via OctoPrint. Use standard G-code instead.

**Reason:** OctoPrint works with standard G-code. Prusa's bgcode format may require additional OctoPrint plugins. If you use bgcode, ensure the OctoPrint bgcode plugin is installed and tested.

## Firmware Requirement

**Minimum:** Prusa Firmware 5.1.0 or higher is required for OctoPrint + Prusa XL.

## Multi-Tool Support

The Prusa XL 5-head multi-tool configuration is supported. Use the [OctoPrintPrusaXL.json](https://github.com/mlbreit/octoprint-prusaxl/blob/main/OctoPrintPrusaXL.json) profile for correct bed dimensions, extruder count, and axes.
