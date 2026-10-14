# Phase 0 paper mockup

Plan: [plan.md](plan.md) · Parts: [bom.md](bom.md) · **Quick start with pens: [pen-disc.md](pen-disc.md)**

## Live reader with an iPhone (Mac)

Double-click **`Open iPhone Reader.command`** (first run sets itself up). With Continuity
Camera (macOS 13+, iOS 16+, same Apple ID) the iPhone shows up as a camera: mount it
15–25 cm above the platter pointing down, press **C** until you see its picture, then
**SPACE** to read. The data disc in the print kit carries a short tune
([`first_light.tune`](print-kit/first_light.tune), 493 bytes of score); the reader plays it
through the Mac's speakers the moment the disc decodes. **R** keeps reading once a second
(try it with the platter spinning), **M** switches to the colour test disc.

A paper disc holds ~1 KB, so it carries a score that the reader synthesises. Real discs
(~29 MB per side) carry full Opus audio. `python tune.py play print-kit/first_light.tune`
plays the tune without a disc.

## Software

A scaled-up paper AURORA disc you can print on any office printer and read with a
cheap camera. Same idea as the real disc (colour cells in rings, a calibration ring,
an index mark), but with 2 mm cells instead of 25 µm, so no microscope is needed.

## Install

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Commands

```bash
python aurora_mock.py capacity                 # how much fits on the paper disc
python aurora_mock.py decode photo.jpg         # read a real photo, writes decoded/
python capture.py esp32 192.168.1.50 -n 5 --decode   # grab from an ESP32 camera and decode
python capture.py usb 0 -n 5 --decode                # same with a USB camera
```

- Print **disc.pdf at 100% / actual size**, never "fit to page". The disc is 7 in
  (177.8 mm) across; cut along the light grey line.
- Capacity: 20 rings, 3,509 cells, 3 bits per cell (cyan, magenta, yellow on or off),
  about 1.1 KB after error correction. A short text file or a tiny image.

## How the disc is laid out

| Ring | Radius (mm) | Job |
| --- | --- | --- |
| Edge | 81.5 to 84.0 | Solid black. The decoder finds the disc and its tilt from this ellipse |
| Index | 78.0 to 80.5 | One black 10° wedge marks angle zero |
| Data | 36 to 76 | 20 rings of 2 mm cells, 8 colours = 3 bits each |
| Calibration | 31 to 35 | All 8 colours, 4 times each. The decoder learns what each colour looks like under *this* light and camera |
| Hole | 3.6 | Fits a standard turntable spindle |

The data is framed with a header, a CRC32 checksum and Reed-Solomon error correction
(32 parity bytes per block), so smudges and a few misread cells are fixed
automatically.

## What decode writes

`decoded/` gets the recovered file plus `diag.png`, the photo with the detected
ellipse and sampling points drawn on top. Look at it first when a decode fails.

## Tested

In simulation (random rotation, tilt, blur, uneven warm light, sensor noise, JPEG):
30 of 30 random trials decode, down to a 640 × 480 photo. Real photos are the next
test; see [the mockup plan](plan.md).
