# AURORA capstone

Print a music disc at home, play it on any turntable.

AURORA (patent pending) stores audio as a pattern of colored ink dots printed on a
12-inch disc. A small camera reader sits beside an ordinary turntable, photographs the
disc as it spins, and turns the dots back into sound. The disc is the artwork and the
album at once.

This repo is where the Drexel capstone team plans, logs experiments and shares
results. Faculty lead: Daniel Belquer, ExCITe Center.

## Target

| Goal | Number |
| --- | --- |
| Playing time | 23 minutes per side |
| Audio quality | Opus at 128 kbps or better |
| Disc | 12 in (305 mm), printed on a desktop UV printer |
| Player | Any turntable at 33⅓ rpm plus the AURORA reader |
| Data cell size | 25 to 30 µm, set by the coupon test |

## Areas

Each area has a folder with its goal, current tasks and hand-offs, so teams can work
in parallel. Areas meet at the specs in [`spec/`](spec/).

| Area | Folder | Lead | Covers |
| --- | --- | --- | --- |
| Materials | [materials/](materials/) | MEM | Disc blanks, inks, coatings, durability |
| Production | [production/](production/) | MEM | UV printer, jigs, print process, quality check |
| Encoder | private repo ([encoder/](encoder/) explains) | Daniel, + NDA students | Conversion software: audio master to print file |
| Reader hardware | [reader-hardware/](reader-hardware/) | MEM + ECE | Device build: optics, light, timing, arm, enclosure |
| Reader software | [reader-software/](reader-software/) | ECE | Firmware: capture, decode, playback |
| Business | [business/](business/) | MIP | Market, pricing, artists, royalties, distribution |
| Financials | [financials/](financials/) | MIP | Budget, purchases, cost per disc |
| Specs | [spec/](spec/) | All | Disc format and print file: the contracts between areas |
| Prototypes | [prototypes/](prototypes/) | All | Phase 0 paper mockup |

## Plan

| Phase | When | Done when |
| --- | --- | --- |
| 0. Set up + mockup | Fall 2026 | Team formed, parts ordered, paper disc decoded from a photo |
| 1. Calibrate | Winter 2027 | Coupon test tells us the smallest dot we can print **and** read |
| 2. First disc | Spring 2027 | One side plays at the senior design showcase |
| 3. Pilot | Summer 2027 | A short run printed for local artists; dual-player prototype (retrofitted Crosley) |

Gate between phases 1 and 2: we do not design the full disc format until the coupon
test gives a cell size we can read at least 99.9% of the time.

## Start here

1. [Pen disc](prototypes/paper-mockup/pen-disc.md): a hand-coloured paper disc on the turntable, read by the Arducam. Start here.
   Then the printed [Phase 0 paper mockup](prototypes/paper-mockup/plan.md).
2. [Phase 1 scope](docs/scope-phase1.md): product targets and what we build first.
   [Roadmap](docs/roadmap.md): the disc, the add-on reader and the dual vinyl/AURORA player.
3. [Coupon test plan](docs/coupon-test.md): the first real experiment, shared by all areas.
4. [Specs](spec/): the disc format and print file every area builds to.
5. [How we work](CONTRIBUTING.md): issues, experiment logs, weekly sync, and what not to post.

## Repo map

```
docs/             scope, plans, meeting notes
spec/             contracts between areas (disc format, print file)
materials/        blanks, inks, coatings, durability
production/       printer, jigs, print process
encoder/          audio -> print file
reader-hardware/  optics, light, timing, mechanics
reader-software/  capture, decode, playback
business/         market, pricing, artists
financials/       budget, purchases, cost per disc
prototypes/       paper mockup
experiments/      one folder per experiment: plan, photos, data, result
```
