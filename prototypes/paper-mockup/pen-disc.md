# Pen disc: test the turntable with paper and pens

The fastest real test: a hand-coloured paper disc on the Crosley, read by the Arducam on
the ESP32. Cells are 10 mm, so the camera sees them easily; the point is to learn about
light, focus, motion blur and colour mix-ups before anything is printed.

## You need

- Letter paper or matte white cardstock, scissors or a craft knife, a 7 mm hole punch
- Coloured pens: Pilot gel pens or markers. Broad tips fill faster
- Arducam + ESP32 running CameraWebServer, a laptop on the same Wi-Fi
- A clamp arm holding the camera 15–25 cm above the platter, a bright lamp

## No printer, no pens? Use the print kit

[`print-kit/aurora_print_kit.pdf`](print-kit/aurora_print_kit.pdf): two letter pages for
Staples or a campus printer. Ask for **colour, matte cardstock (110 lb), 100% / actual
size, no "fit to page"**, and check the 100 mm bar with a ruler.

- Page 1, colour test disc: 167 printed cells, 6 colours + white. Analyze with
  `python pen_test.py analyze photo.jpg --key print-kit/colour_disc_key.json`
- Page 2, data disc: carries `print-kit/message.txt`. Read it with
  `python aurora_mock.py decode photo.jpg`

Need a different message or tune on the data disc? Ask Daniel: the encoder is private.

## 1. Make the disc (about 20 min)

```bash
pip install -r requirements.txt
python pen_test.py template --pens black,blue,red,green     # list YOUR pen colours
```

Print `pen_disc.pdf` at **100% / actual size**. The black ring should measure 168 mm.
Colour every cell with the pen whose letter is printed in it; leave `·` cells white.
Colour the big calibration slots in the inner ring the same way. Fill solidly, edge to
edge. Cut on the grey circle and punch the centre hole. Keep `pen_disc_key.json`: it is
the answer sheet.

## 2. Still test

Platter stopped, lamp at about 45° so its reflection misses the lens (gel ink is shiny).

```bash
python capture.py esp32 <ESP32-IP> -n 5
python pen_test.py analyze shots/*.jpg --rpm 0 --log ../../experiments/pen-disc/results.csv
```

Each photo gets a score (% of cells right) and a `_diag.jpg`: green rings are right,
red rings are wrong. Aim for 100% before spinning.

## 3. Spinning tests

The Crosley does 33⅓, 45 and 78 rpm. For each speed:

1. Automatic exposure: `python capture.py esp32 <IP> -n 5 --auto`
2. Short manual exposure, lamp as close as possible:
   `python capture.py esp32 <IP> -n 5 --exposure 20` (try 100, 50, 20, 10)
3. Analyze with `--rpm 33` (or 45, 78) and `--note "exposure 20"`.

The analyzer also reports **smear in mm**: how far the disc moved while the shutter was
open, measured on the black index wedge. Plot smear against exposure and speed.

## What to expect

- 10 mm cells survive a lot of smear, so scores may stay high even when photos look blurry.
- The circle may come out skewed when spinning: the camera reads the image top to bottom
  while the disc turns (rolling shutter). Note when the disc stops being found.
- Real AURORA cells are 25 µm, 400× smaller. Any smear you measure here, divided by
  0.025 mm, is how many real cells it would blur. That is the case for a global-shutter
  camera and a 10 µs flash.

## Try next

- `--cell 8` for more, smaller cells; then 6.
- More pens: `--pens black,blue,red,green,purple,orange,pink`. Watch which pairs get mixed up.
