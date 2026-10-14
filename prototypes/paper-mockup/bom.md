# Phase 0 parts: paper mockup

Goal: print a big-cell paper disc, photograph it, decode it. See the
[mockup plan](plan.md).

| # | Part | Status | Use | Approx. price |
| --- | --- | --- | --- | --- |
| 1 | Arducam camera | **On hand** | Takes the photo | – |
| 2 | ESP32 | **On hand** | Runs the camera, sends JPEGs to the laptop over Wi-Fi | – |
| 3 | Crosley turntable | **On hand** | Platter and spindle for the disc; spinning test in stage B | – |
| 4 | Laptop with Python 3.10+ | On hand | Runs the encoder and decoder | – |
| 5 | Colour printer (inkjet or laser) | Lab / library | Prints the 7 in disc at 100% scale | – |
| 6 | Matte white cardstock, 65–110 lb, letter size | Buy | Stiff, flat, no glare. Glossy photo paper reflects the light back into the lens | $10 |
| 7 | Gooseneck or articulated clamp arm with a 1/4-20 screw | Buy | Holds the camera 15 to 25 cm above the platter, pointing straight down | $15 |
| 8 | LED desk lamp or small LED panel, high CRI (90+) if possible | Buy or borrow | Even, steady light. Avoid fluorescent tubes: they flicker | $15 |
| 9 | Phone | On hand | Backup camera and a reference shot for every ESP32 shot | – |
| 10 | Craft knife, cutting mat, 7 mm hole punch | Lab | Cut the disc out and punch the spindle hole | – |

**Phase 0 extra spend: about $40.**

### Which Arducam?

The software works with any of these. Write the exact model in the first meeting notes.

| If you have | Connect it like this |
| --- | --- |
| ESP32-CAM board, or ESP32-S3 with an OV2640 / OV5640 module | Flash the Arduino example *ESP32 → Camera → CameraWebServer*, set frame size to UXGA (1600 × 1200), then `python capture.py esp32 <ip>` |
| Arducam Mini (SPI) wired to a plain ESP32 | Flash the ArduCAM library's ESP32 web-server example. If its URL differs from `/capture`, save the JPEG by hand and run `aurora_mock.py decode` |
| Arducam USB camera | Plug it into the laptop: `python capture.py usb 0` |
