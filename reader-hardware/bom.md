# Reader parts list (prototype)

About $205 for one reader. The Pi 5 does everything, timing included.
Prices checked October 2026; confirm before ordering.

| Part | Pick | Why | Approx. price |
| --- | --- | --- | --- |
| Camera | [Raspberry Pi Global Shutter Camera](https://www.pishop.us/product/raspberry-pi-global-shutter-camera/) (Sony IMX296, colour, 1456 × 1088, 3.45 µm pixels) | Global shutter: the whole frame exposes at once, so a spinning disc does not smear. Has an external trigger input | $55 |
| Lens | Raspberry Pi 16 mm C-mount lens + 5 mm C-mount extension ring | About 0.35× magnification = about 10 µm of disc per pixel, 62 mm working distance. Run near f/2.8 | about $60 |
| Computer | Raspberry Pi 5, 2 GB | Takes the camera at full speed; enough CPU to unwrap, classify, correct errors and decode audio | [about $65](https://magazinmehatronika.com/en/the-2026-raspberry-pi-pricing-and-buying-guide/) |
| Timing | The Pi 5's hardware PWM pin | One pulse train drives both the camera trigger and the LED, so each frame gets exactly one flash. Hardware PWM has no Linux timing jitter | $0 |
| Audio | PCM5102A I2S DAC board, DPDT signal relay + driver transistor, 2× RCA jack pairs | Line out, and automatic turntable/AURORA switching | about $15 |
| Light cone | Black PETG print + black flock paper | Blocks room light; no contact with the disc | about $5 |
| Cable + cooling | Pi 5 camera cable (22-pin to 15-pin) and Pi 5 Active Cooler | The camera ships with the older cable; the cooler stops throttling under load | about $7 |
| Light | 1–2 white high-CRI LEDs, logic-level MOSFET, linear polarizer film | 10 µs flash freezes motion; crossed polarizers make bare aluminum look black so ink stands out | about $20 |

## If the camera is out of stock

1. Try other stockists first: Farnell, Adafruit, DigiKey, Mouser, PiShop, Amazon.
2. Arducam OV9782: colour global shutter, 1280 × 800, 3 µm pixels. Check that the
   listing says Raspberry Pi 5 support.
3. A rolling-shutter camera such as the IMX462 (cheaper) only works inside a
   light-tight hood, with the exposure longer than the sensor's readout and one short
   flash while every row is exposing. Expect about 25–30 frames per second and buy
   the version with an IR-cut filter.

## Notes

- **Trigger hack:** the camera's external trigger needs one small surface-mount
  resistor removed (R11) and two wires soldered to the XTR and GND pads. XTR is a
  1.8 V input, so feed it from the Pi's 3.3 V PWM pin through a resistor divider.
  The pulse width sets the exposure; check the trigger polarity in the docs. Steps are in the
  [Raspberry Pi camera documentation](https://www.raspberrypi.com/documentation/accessories/camera.html).
- **Why not a rolling-shutter camera:** it scans line by line, so a moving disc
  smears. Use it for setup photos only.
- **Why not an ESP32-P4 yet:** its supported camera list has no colour global-shutter
  sensor. A later low-cost version could use a mono sensor with red, green and blue
  flashes in turn.
- **Upgrade path if focus is the problem:** a 0.35× telecentric lens gives far more
  depth of field, but costs about $800 to $1,200. Only if the cheap lens fails the
  focus study.
