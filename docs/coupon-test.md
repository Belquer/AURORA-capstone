# Coupon test plan

The first shared experiment. MEM prints, ECE reads, MIP turns the result into minutes
of audio.

## The coupon

A disc (or a 100 × 100 mm flat tile for the static stage) carrying **dot ladders**:
rows of square cells at decreasing sizes.

| Parameter | Values |
| --- | --- |
| Cell sizes | 50, 40, 30, 25, 20 µm |
| Inks | C, M, Y alone; C+M, C+Y, M+Y; C+M+Y; blank |
| Pattern per ladder | Checkerboard and a random pattern of known bits, 2,000 cells each |
| Substrates | Bare aluminum, white-primed aluminum, acrylic |
| Fiducials | Corner marks on every ladder so software can find it |

The random patterns come from a fixed seed so the reader can compare against the
truth. The generator is private; Daniel provides the print files.

## Stage A: still

1. Photograph each ladder under the reader camera, stationary, at the planned
   magnification (about 10 µm of disc per pixel).
2. Try lighting: plain white LED; white LED with crossed polarizers.
3. Classify each cell's colour; count errors against the known pattern.

## Stage B: spinning

1. Mount the coupon on a turntable at 33⅓ rpm.
2. Strobe the LED for 10 µs, synced to the camera trigger.
3. Repeat the classification at several radii (inner, middle, outer).

## Stage C: focus

1. Raise and lower the coupon in 0.1 mm steps through ±1 mm.
2. Record the error rate at each height for each cell size.
3. Separately, measure the vertical wobble of two real turntables with a dial gauge
   or laser distance sensor.

## Stage D: durability

Nothing touches the data during play, so playing does not wear the disc. Handling,
light and heat do. Run each test on fresh coupons, then read them under the reader
and log the error rate. A coupon passes if it still decodes with error correction to
spare.

| Test | Method | What it tells us |
| --- | --- | --- |
| Ink adhesion | Cross-hatch tape test, ASTM D3359 | Does the ink stay on each substrate and primer? |
| Rub resistance | Sutherland rub, ASTM D5264, with and without a clear top coat | How much handling the cells survive |
| Fingerprints and cleaning | Press a thumb on the data, read, wipe with a microfibre cloth, read again | Whether error correction absorbs everyday handling |
| Light fastness | Xenon-arc exposure, ISO 4892-2 or ASTM G155 | How fast the inks fade, and how the error rate changes as they do |
| Heat and humidity | Cycle between about 5 °C and 60 °C at high humidity; also 2 h at 65 °C (a car in summer) | Ink cracking, warp, and whether the disc stays within focus (about ±0.2 mm) |
| Flatness | Measure warp with a dial gauge before and after each test | Which blank thickness and material stays flat |
| Follower wear | 1,000 passes of a light (a few grams) PTFE or nylon follower tip on one guide track | Wear on the guide and on any data near it |

## What we record

One row per run in `experiments/coupon/results.csv`:

```csv
date,substrate,ink,cell_um,stage,radius_mm,height_offset_mm,lighting,durability_test,cells,errors,error_rate,notes
```

## Pass criterion

A cell size passes when its error rate is **below 1 in 1,000** (0.1%) at every radius
and over the height range a real turntable produces. Error correction handles the
rest. The smallest passing size becomes the Phase 2 design point.
