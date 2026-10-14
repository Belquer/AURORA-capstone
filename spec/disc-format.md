# Disc format v0 (draft)

Numbers marked TBD are set by the coupon test or by Daniel.

## Physical

| Item | Value |
| --- | --- |
| Diameter | 305 mm (12 in) |
| Centre hole | 7.24 mm (standard spindle) |
| Thickness | 0.75–1.5 mm, set by the materials tests |
| Flatness | Within ±0.2 mm on the platter (lens depth of field) |
| Sides | Two; each side is self-contained (own centring and index marks) |

## Layout (each side)

| Item | Value |
| --- | --- |
| Outer edge ring | Solid black, for finding the disc |
| Index mark | Black wedge at angle 0 |
| Data region | Outer radius 145 mm; inner radius ~25 mm (set by the reader's light cone clearing the spindle) |
| Cells | Square, pitch TBD (25–30 µm expected), concentric rings |
| Colour states | Cyan, magenta, yellow on/off = 3 bits per cell (4 levels each = 6 bits, if the coupon test allows) |
| Sync | Radial sync marks at fixed angles, carrying track and sector address |
| Calibration | Patches of every colour state, read each play |
| Guide feature | None. A motorised reader arm moves the camera; the disc is flat |
| Track rings | A solid black ring, 0.8 mm wide, where each track starts, so listeners can see the tracks (like the gaps on vinyl) |

## Data

| Item | Value |
| --- | --- |
| Audio | Opus, 48 kHz stereo, 128 kbps target |
| Error correction | Reed-Solomon in the mockup; layout across the disc TBD (Daniel) |
| Addressing | Every block addressed, so blocks can be read in any order |
