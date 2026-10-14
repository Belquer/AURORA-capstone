# Phase 1 scope: prove we can print and read the dots

Phase 1 answers one question before anyone designs a full disc: **what is the
smallest colored dot we can print on a disc and still read reliably while it spins?**
That one number sets playing time, bit rate and every later design choice.

## Why this comes first

Capacity grows with the square of the dot size. Halving the cell from 50 µm to 25 µm
gives four times the data. At 25 µm with three ink colors we fit about 23 minutes of
high-quality audio per side; at 50 µm, about 6. So we measure before we design.

## Product targets (what every decision is checked against)

| Target | Number |
| --- | --- |
| Playing time | 23 minutes per side or more |
| Audio | 48 kHz stereo, Opus 128 kbps or better, from a 24-bit master |
| Needle drop to sound | Under 2 seconds, including dropping mid-album |
| Cost per disc | $5 or less, both sides, materials plus printer time |
| Wear | None from playing: nothing touches the data |
| Turntable | Any turntable at 33⅓ rpm; its speed wobble must not be audible |

## What Phase 1 delivers

| # | Deliverable | Lead | Done when |
| --- | --- | --- | --- |
| 1 | Coupon disc set: dot ladders printed in each ink and in ink combinations | MEM | 3 substrates printed, photographed under the microscope |
| 2 | Static reader: camera, lens and light on a fixed stand | ECE + MEM | Reads a still coupon, cell colors classified |
| 3 | Spinning reader: same rig over a turntable, with strobe | ECE | Reads a coupon at 33⅓ rpm without motion blur |
| 4 | Focus study: depth of field versus disc wobble | MEM | We know how much height change the lens tolerates and how much a real turntable produces |
| 5 | Error-rate report: bit errors per cell size and ink | ECE | A table and a recommended cell size |
| 6 | Audio budget: what fits at that cell size | MIP | Minutes per side at 3 quality levels, with listening tests |

## Out of scope for Phase 1

- The full disc layout, sync marks and error correction (Phase 2).
- Guide grooves or ridges (Phase 2).
- The final enclosure and product design.

## The known hard problem

To resolve 25 µm cells the lens must stay near f/2.8, which leaves only about
±0.2 mm of focus depth. A cheap turntable plus a slightly warped disc can move more
than that. Deliverable 4 exists to measure this early. Candidate fixes, cheapest
first: a skid that rides the disc so the lens follows it, larger cells, a liquid
autofocus lens, a telecentric lens.
