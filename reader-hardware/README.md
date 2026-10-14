# Reader hardware (device build)

**Owner:** MEM (mechanics, optics) + ECE (electronics) · **Works with:** reader-software

**Goal:** a reader that sits beside any turntable and images the spinning disc sharply.

Parts list: [bom.md](bom.md) (about $205; Raspberry Pi 5 + Global Shutter Camera).

## Subsystems

| Subsystem | Target |
| --- | --- |
| Optics | 16 mm C-mount lens, ~0.35× magnification, ~10 µm of disc per pixel, near f/2.8 |
| Focus | Depth of field about ±0.2 mm: measure real disc and platter wobble |
| Light | White high-CRI LEDs, 10 µs flash, crossed polarizers |
| Timing | One Pi 5 hardware-PWM pulse drives camera trigger and LED together |
| Mechanics | **Motorised arm** (stepper or servo) that clamps beside the turntable and steps the camera inward ~8 mm per turn; position comes from the addresses read off the disc. No guide on the disc, no stylus |
| Light cone | Matte-black cone from lens to disc, open bottom ~30 mm, 2 mm air gap above the disc (no contact), flocked inside |
| Audio switch | RCA in from the turntable, RCA out to the amp; a relay picks turntable or AURORA automatically |

## Light cone

- Height ~60 mm (lens working distance), bottom opening ~30 mm: the camera sees
  ~15 × 11 mm (18.6 mm diagonal) and the flash LEDs sit inside near the bottom, angled in.
- **Never touches the disc.** Keep a ~2 mm gap so disc warp (up to ~1 mm) and dust pass
  under it. The flash outshines what leaks through the gap.
- Matte black 3D print, lined with black flock paper so the inside does not reflect.
  Polarizer film over the LEDs and over the lens.
- **Watch the spindle and record weights.** The spindle stands ~10–15 mm above the disc.
  A round 30 mm cone cannot get closer than about 20–25 mm to the centre; notch the
  inner side of the cone if we want data closer in.

## Audio out

The Pi 5 has no headphone jack. The reader offers two outputs:

| Output | How | Works with |
| --- | --- | --- |
| Bluetooth (default) | Pi 5 built-in Bluetooth, no extra parts | Crosley models with Bluetooth in, any Bluetooth speaker or headphones |
| Line out, 3.5 mm | I2S DAC board (PCM5102A, ~$6–25) or a USB DAC dongle (~$10) | Crosley **AUX IN**, powered speakers, any amp |

### Automatic switching between vinyl and AURORA

The reader sits in the audio chain: **turntable RCA out -> reader RCA in -> reader RCA
out -> amp or powered speakers.**

- A small signal relay (DPDT, gold contacts) on a Pi GPIO pin picks the source.
- **Normally closed = turntable passes straight through**, so vinyl still plays if the
  reader is off or unplugged.
- The Pi switches to AURORA when the camera sees an AURORA disc (edge ring and index
  mark) and playback starts, and back when it stops. Mute the DAC for ~50 ms around each
  switch so it does not click.
- The turntable output must be **line level** (built-in preamp on, as on most Crosleys).
  A phono-level output into the reader would need its own preamp.
- Prototype shortcut: a passive mixer (one 10 kΩ resistor per source per channel into
  the RCA out). Whichever source is silent simply adds nothing. Costs ~6 dB of level.

The turntable's own tone arm stays parked during AURORA play; its platter only spins the disc. Bluetooth
adds ~0.2 s of delay, which only adds to the time before the first sound.

## Now

- [ ] Order the camera, Pi 5 camera cable, lens, extension tubes, Active Cooler, I2S DAC.
- [ ] Check our Crosley's back panel: AUX IN? Bluetooth in? RCA out at line level?
- [ ] MEM: 3D-print a first light cone; measure light leakage with the flash off.
- [ ] ECE: relay board on a GPIO pin, RCA in/out jacks; test passthrough with the Pi off.
- [ ] ECE: 60 Hz PWM with 10 µs pulses from the Pi 5 on a scope.
- [ ] MEM: measure platter wobble on two turntables (dial gauge).
- [ ] MEM + ECE: motorised arm prototype (small stepper or hobby servo, 3D-printed arm, table clamp); test on the paper data disc.

## Hands off

- Frame format and timing to [reader-software](../reader-software/).
