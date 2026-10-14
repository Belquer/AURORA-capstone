# Reader software (firmware)

**Owner:** ECE · **Works with:** reader-hardware, encoder

**Goal:** turn camera frames into music, starting within 2 seconds of the reader landing.

## Architecture (agreed)

- **Read ahead, play from memory.** The camera stays at least ~10 s ahead of the music
  and stores decoded audio in memory (1–2 frames per second are enough; see
  [roadmap](../docs/roadmap.md)). Playback is clocked by the Pi,
  not by the platter, so turntable speed wobble is inaudible, and a spot spoiled by
  dust or a bump is re-read on the next turn.
- **Start fast.** Needle drop to sound under 2 seconds, also mid-album. Decoding starts
  on the first frames; there is no scanning step the listener sees.

## Where the code lives

- **Public (here):** capture, hardware control, app and UI, playback, and the *paper*
  disc decoder used for teaching.
- **Private, NDA only (`Belquer/AURORA-core`):** the production decoder library (locate,
  unwrap, classify, sync, error correction for the real format).

## Modules

```
capture       Picamera2, external-trigger mode, frame timestamps
locate        find the disc centre and angle (edge ring, index mark)
unwrap        map pixels to (radius, angle) and to cells
classify      cell colour -> bits
sync          sync marks -> track and sector address
decode        error correction -> audio packets in address order
play          Opus decode -> audio out (I2S DAC or USB), clocked by the Pi
ui            buttons, status LED
```

The paper mockup decoder ([prototypes/paper-mockup](../prototypes/paper-mockup/))
already covers locate, unwrap, classify and decode for still photos.

## Now

- [ ] Picamera2 with the Global Shutter Camera in external-trigger mode; log frame timing.
- [ ] Run the mockup decoder on frames from the real camera (paper disc, platter stopped).
- [ ] Measure decode time per frame on the Pi 5.
