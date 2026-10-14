# Product roadmap

Three products share one disc format.

| Product | What it is | Who it is for | Phase |
| --- | --- | --- | --- |
| **AURORA disc** | Printed 12 in disc, both sides, ~$1–3 to make | Artists, labels, fans | 1–3 |
| **AURORA reader** | Add-on that sits beside any turntable; the turntable only spins the disc | People who already own a turntable | 1–2 |
| **AURORA dual player** | One turntable that plays vinyl records *and* AURORA discs | New buyers; the "record player of the future" | 3 (prototype), later product |

## Reading strategy (applies to both players)

The reader only needs to stay **about 10 seconds ahead** of the music.

- The data rate is small: 23 minutes at Opus 160 is ~170 kbps, about 75,000 cells per
  second. One camera frame holds ~250,000 cells, so **1–2 frames per second** keep up.
- The arm moves slowly inward as the music plays, like a tone arm, and shows how far into
  the side you are.
- A frame spoiled by dust or a bump is re-read on the next turn (1.8 s later); a 10 s
  buffer allows ~5 retries.
- Sound still starts ~2 s after the reader lands. To skip, the arm jumps to the black
  ring at the start of the next track.
- Consequences: a slow, cheap computer (Pi Zero 2 W) is enough, the flash fires 1–2 times
  per second, and only a few hundred KB of memory are needed.

## AURORA dual player

A turntable with **two arms on one platter**:

```
          +-------------------------------------+
          |  [camera arm]       ( disc )   [tone arm + stylus]
          |   AURORA reader    platter      vinyl, as usual
          |                                     |
          |  disc-type detection -> audio switch -> DAC / phono preamp
          |                     -> amplifier -> speakers, line out, Bluetooth
          +-------------------------------------+
```

- **Plays vinyl** with a normal tone arm and cartridge.
- **Plays AURORA** with the camera arm; the stylus stays parked.
- **Knows which is which**: the camera sees an AURORA disc's edge ring and index mark;
  anything else is treated as vinyl.
- **One audio path**: built-in phono preamp for vinyl, DAC for AURORA, one amplifier,
  speakers, line out and Bluetooth. Solves the "no AUX input" problem of suitcase players.

### Prototype (Phase 3): retrofit the Crosley

Mount the reader's camera arm on the side opposite the Crosley's tone arm and feed the
reader's audio into the Crosley's internal amplifier through the relay. Same parts as the
reader prototype plus a mounting plate. MEM + ECE.

### Product cost estimate (1,000+ units)

| Block | Approx. |
| --- | --- |
| Turntable mechanism: motor, platter, plinth, tone arm, cartridge, phono preamp | $20–35 |
| Reader module: computer, camera, lens, light, cone, arm motor | $35–70 |
| Shared audio: DAC, amplifier, speakers, Bluetooth | $10–20 |
| Housing, power, assembly and test | $15–25 |
| **Bill of materials** | **~$80–150** |
| Likely shop price (2.5–4× BOM) | ~$199–349 |
