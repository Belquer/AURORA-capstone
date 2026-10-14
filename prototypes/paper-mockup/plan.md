# Phase 0 mockup: a paper disc we can read

Before anything is printed with a UV printer, we build the whole chain at a scale
where nothing is hard: **file → colour disc → photo → file**. Cells are 2 mm instead
of 25 µm, the disc is paper, and the camera is the Arducam we already have.

It gives every team something real in the first two weeks:

- **ECE** gets a working decoder to read, break and improve.
- **MEM** gets the mounting, lighting and spinning problems in miniature.
- **MIP** gets a first object to hold, and a feel for what "1 KB per disc" means
  next to "23 minutes of audio".

Parts: [bom.md](bom.md). Software: [README.md](README.md).

## Stage A: still photo (week 1)

1. **Get the disc.** Use the data disc on page 2 of
   [`print-kit/aurora_print_kit.pdf`](print-kit/aurora_print_kit.pdf). The encoder is private;
   ask Daniel for a disc with different content.
2. **Print.** Print page 2 on matte cardstock at **100% / actual size**. Measure
   the black ring with a ruler: it should be 168 mm across. If not, the printer scaled it.
3. **Cut.** Cut along the light grey circle; punch the centre hole.
4. **Mount.** Put the disc on the turntable platter. Clamp the camera 15 to 25 cm
   above it, looking straight down, with the whole disc in the frame. Light from the
   side at about 45° so the lamp's reflection misses the lens.
5. **Shoot and decode.** `python capture.py esp32 <ip> -n 5 --decode` (or `usb 0`).
   Take the same shot with a phone as a reference.
6. **Log it.** One row per photo in `experiments/mockup/results.csv`.

**Pass:** 5 photos in a row decode with the platter stopped.

When a decode fails, open `decoded/diag.png`. The green ellipse should sit on the
black ring, the red line should point at the black wedge, and the dots should sit in
the middle of the cells. Red dots are the cells the decoder was least sure of.

## Stage B: spinning (week 2)

Same rig, platter on at 33⅓ rpm. **We expect this to fail**, and the point is to
measure how.

At the outer data ring the paper moves about 0.27 m/s, so one 2 mm cell passes in
about 7.5 ms. Two things go wrong with a cheap camera:

- **Blur:** an exposure longer than about 1 ms smears each cell into its neighbours.
  More light lets the camera use a shorter exposure.
- **Rolling shutter:** the sensor reads the image top to bottom over tens of
  milliseconds, so the disc turns while the picture is being taken. The circle comes
  out skewed.

Try, in order, and log each:

1. Platter on, room light.
2. Platter on, lamp as close and bright as possible.
3. Platter on, ESP32 camera exposure set to manual and as short as it goes.
4. Same with the phone in burst or slow-motion mode.

Save `diag.png` for every run. These pictures are the argument for the Phase 1
global-shutter camera with a strobe, so keep the good failures.

## Stage C: stretch goals

- **Smaller cells.** Change `CELL` in `aurora_mock.py` to 1.5 mm, then 1.0 mm. Find
  where the Arducam stops reading a still disc. It is our first real "smallest
  readable cell" number, at paper scale.
- **Lighting.** Compare white LED, warm desk lamp and daylight. Watch the colour
  margin the decoder prints.
- **Paper.** Matte cardstock against glossy photo paper against plain copy paper.

## What we record

`experiments/mockup/results.csv`, one row per photo:

```csv
date,stage,camera,resolution,cell_mm,rpm,lighting,exposure,decoded,margin_p1,notes
```

`margin_p1` is the "weakest-cell color margin" number the decoder prints. Higher is
safer; watch it fall as conditions get worse.

## Done when

- Stage A passes, with the photo set and `diag.png` files in `experiments/mockup/photos/`.
- Stage B has a logged result for each of the four tries.
- One paragraph in `experiments/mockup/result.md`: what failed when spinning, and why.
