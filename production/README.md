# Production (printing and equipment)

**Owner:** MEM · **Works with:** materials, encoder, financials

**Goal:** turn a print file into a finished disc on the UV printer, repeatably, in
10–20 minutes per side.

## Equipment

| Item | Status | Use |
| --- | --- | --- |
| HeyGears G1X UV printer | Loan proposal sent | Prints the cells; flatbed 420 × 330 mm fits one 12 in disc |
| Centre-pin jig | To design | Locates the blank by its spindle hole on the print bed. Each side has its own centring marks, so the two sides need not line up |
| Scale, 0.01 g | To buy | Weigh ink use per disc |
| Dial gauge on a stand | To buy | Flatness before and after printing |
| Loupe or USB microscope | To buy | Check dots after each print |

## Cutting discs from sheets

- Diameter **302 mm** (LP standard), centre hole **7.24 mm**. A 12 × 12 in sheet
  (304.8 mm) leaves only ~1.4 mm each side, so hold it down well.
- **Hole first, outline second, cut around the hole.** The hole must be centred to
  ~0.1 mm or the disc wobbles under the reader.

| Method | Cost | Good for |
| --- | --- | --- |
| Drill the hole, then a beam-compass circle cutter pivoting on a pin in the hole | $20–40 | Prototypes up to ~0.75 mm PET; slow |
| Desktop CNC router, 400 × 400 mm (e.g. Genmitsu 4040 PRO), single-flute O-flute bit | ~$400–700 | **Default.** PET, ABS, acrylic, thin aluminium; hole and outline in one setup; ~2–4 min per disc |
| Steel-rule die with built-in centre punch + press, or outsourced die-cutting | die ~$100–250 | Volume: seconds per disc |

**Do not laser-cut PVC/vinyl** (releases chlorine gas, ruins the machine) or ABS (toxic
fumes). PET melts under a laser. Lasers are only good for acrylic.

## Process (draft)

1. Clean the blank; adhesion wipe if the material needs it.
2. Place on the centre-pin jig.
3. Print side A from the print file; UV cure.
4. Flip, print side B.
5. Optional clear top coat.
6. Read on the reader: the disc passes if it decodes with error correction to spare.

## Now

- [ ] Design and print the centre-pin jig.
- [ ] Time every pass and weigh the ink on the first coupon print.
- [ ] Find the G1X print mode that gives the smallest clean dot.

## Hands off

- Print time and ink per disc (colour data and track rings only; no guide) to [financials](../financials/).
- Printer resolution and mode limits to [spec/print-file.md](../spec/print-file.md).
