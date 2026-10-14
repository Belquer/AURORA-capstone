#!/usr/bin/env python3
"""Hand-coloured pen disc: test the Arducam, the light and the turntable before any printing.

  python pen_test.py template                      # pen_disc.pdf (letter page) + pen_disc_key.json
  python pen_test.py template --pens black,blue,red,green,purple --cell 8
  python pen_test.py analyze photo.jpg             # read a photo, score it against the key
  python pen_test.py analyze shots/*.jpg --rpm 33 --log ../../experiments/pen-disc/results.csv
  python pen_test.py simulate                      # fake still + spinning photos, no camera needed

Colour each cell with the pen whose letter is printed in it. Leave cells marked with a
dot white. Colour the calibration ring too: each pen fills the slots with its letter.
"""
import argparse, csv, json, math, sys, time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aurora_mock import (DISC_R, EDGE_IN, EDGE_OUT, INDEX_IN, INDEX_OUT, INDEX_DEG, HOLE_R,
                         find_disc, make_mapper, sample)

CAL_IN, CAL_OUT = 26.0, 34.0          # big calibration slots, easy to colour
DATA_IN, DATA_OUT = 38.0, 76.0
PAGE_DPI = 300
KNOWN = {  # typical gel-pen colours on white paper, used only by `simulate` and the legend
    "black": (35, 35, 40), "blue": (40, 70, 170), "red": (200, 40, 50), "green": (30, 140, 70),
    "purple": (110, 50, 150), "pink": (230, 90, 160), "orange": (240, 120, 40),
    "lightblue": (60, 160, 220), "brown": (120, 70, 40), "yellow": (240, 210, 40),
}
WHITE = ("white", ".", (245, 245, 240))
PRINT_RGB = {  # saturated colours for printed (not hand-coloured) test discs
    "black": (20, 20, 20), "blue": (25, 75, 200), "red": (225, 35, 40), "green": (15, 150, 60),
    "purple": (125, 45, 170), "orange": (250, 140, 15), "yellow": (250, 215, 0), "cyan": (0, 170, 230),
    "magenta": (225, 0, 140),
}


def pen_codes(names):
    used, out = set(), []
    for n in names:
        code = "K" if n == "black" else next(ch.upper() for ch in n + "XYZQ" if ch.upper() not in used and ch.upper() != "K")
        used.add(code)
        out.append((n, code, KNOWN.get(n, (128, 128, 128))))
    return out


def layout(cell):
    rings, r = [], DATA_IN
    while r + cell <= DATA_OUT + 1e-6:
        rc = r + cell / 2
        rings.append({"r0": r, "r1": r + cell, "n": int(2 * math.pi * rc // cell)})
        r += cell
    return rings


# ------------------------------------------------------------------ template
def template(pens, cell, seed, out, filled=False):
    pens = pen_codes(pens)
    classes = pens + [WHITE]
    rings = layout(cell)
    rng = np.random.default_rng(seed)
    n_cells = sum(rg["n"] for rg in rings)
    key = [classes[i][1] for i in rng.permutation(np.arange(n_cells) % len(classes))]
    cal = [c[1] for c in classes] * 2

    W, H = int(8.5 * PAGE_DPI), int(11 * PAGE_DPI)
    px = PAGE_DPI / 25.4
    cx, cy = W / 2, 0.45 * PAGE_DPI + DISC_R * px
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", int(cell * px * 0.32))
        small = ImageFont.truetype("DejaVuSans.ttf", 34)
        bold = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
    except OSError:
        font = small = bold = ImageFont.load_default()

    def poly(r0, r1, a0, a1):
        angs = np.linspace(math.radians(a0), math.radians(a1), max(2, int(abs(a1 - a0) / 2) + 2))
        pts = [(cx + r1 * px * math.cos(a), cy - r1 * px * math.sin(a)) for a in angs]
        pts += [(cx + r0 * px * math.cos(a), cy - r0 * px * math.sin(a)) for a in angs[::-1]]
        return pts

    def label(r, a, text, f, fill=(150, 150, 150)):
        x, y = cx + r * px * math.cos(math.radians(a)), cy - r * px * math.sin(math.radians(a))
        d.text((x, y), text, font=f, fill=fill, anchor="mm")

    d.ellipse([cx - DISC_R * px, cy - DISC_R * px, cx + DISC_R * px, cy + DISC_R * px], outline=(225, 225, 225), width=3)
    d.polygon(poly(EDGE_IN, EDGE_OUT, 0, 360), fill=(0, 0, 0))
    d.polygon(poly(INDEX_IN, INDEX_OUT, 0, INDEX_DEG), fill=(0, 0, 0))
    rgb_of = {c: PRINT_RGB.get(n, rgb) for n, c, rgb in pens}
    k = len(cal)
    for i, code in enumerate(cal):
        fillc = rgb_of.get(code) if filled else None
        d.polygon(poly(CAL_IN, CAL_OUT, i * 360 / k, (i + 1) * 360 / k), fill=fillc, outline=(170, 170, 170), width=2)
        if not filled:
            label((CAL_IN + CAL_OUT) / 2, (i + 0.5) * 360 / k, code, font)
    i = 0
    for rg in rings:
        for j in range(rg["n"]):
            a0, a1 = j * 360 / rg["n"], (j + 1) * 360 / rg["n"]
            fillc = rgb_of.get(key[i]) if filled else None
            d.polygon(poly(rg["r0"], rg["r1"], a0, a1), fill=fillc, outline=(200, 200, 200), width=2)
            if not filled:
                label((rg["r0"] + rg["r1"]) / 2, (a0 + a1) / 2, key[i], font, (165, 165, 165))
            i += 1
    d.ellipse([cx - HOLE_R * px, cy - HOLE_R * px, cx + HOLE_R * px, cy + HOLE_R * px], outline=(0, 0, 0), width=4)

    y = cy + DISC_R * px + 70
    title = "AURORA colour test disc" if filled else "AURORA pen disc"
    d.text((W / 2, y), f"{title}  ·  print at 100% (actual size), cut on the grey circle", font=bold, fill=(0, 0, 0), anchor="mm")
    y += 75
    if filled:
        leg = f"{len(pens)} printed colours + white · {len(key)} cells of {cell:g} mm · analyze with pen_test.py and this key"
    else:
        leg = "   ".join(f"{c} = {n}" for n, c, _ in pens) + "   · = leave white"
    d.text((W / 2, y), leg, font=small, fill=(0, 0, 0), anchor="mm")
    y += 60
    d.text((W / 2, y), "Matte paper or cardstock. Punch the centre hole." if filled else
           "Fill every cell solidly, edge to edge. Colour the calibration ring (inner, big slots) too.",
           font=small, fill=(60, 60, 60), anchor="mm")
    y += 50
    d.text((W / 2, y), f"Check: the black ring should measure {2 * EDGE_OUT:.0f} mm across. Key: {Path(out).stem}_key.json (seed {seed}).",
           font=small, fill=(60, 60, 60), anchor="mm")
    img.save(out, dpi=(PAGE_DPI, PAGE_DPI))
    img.save(Path(out).with_suffix(".pdf"), resolution=PAGE_DPI)
    keyfile = Path(out).with_name(Path(out).stem + "_key.json")
    keyfile.write_text(json.dumps({"pens": [{"name": n, "code": c} for n, c, _ in pens],
                                   "cell_mm": cell, "seed": seed, "rings": rings, "cells": key, "cal": cal}, indent=1))
    print(f"{n_cells} cells, {len(pens)} pens + white. Wrote {out}, {Path(out).with_suffix('.pdf')} and {keyfile}.")


# ------------------------------------------------------------------ analyze
def read_disc(photo, keyd):
    bgr = cv2.imread(str(photo))
    if bgr is None:
        raise SystemExit(f"cannot read {photo}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    center, axes, ang = find_disc(rgb)
    px_per_mm = (axes[0] + axes[1]) / 2 / EDGE_OUT
    gray = cv2.cvtColor(cv2.GaussianBlur(rgb, (5, 5), 0), cv2.COLOR_RGB2GRAY)
    m0 = make_mapper(center, axes, ang, 0.0)
    th = np.arange(0, 360, 0.25)
    x, y = m0(np.full_like(th, (INDEX_IN + INDEX_OUT) / 2), th)
    prof = sample(gray, x, y)
    hi, lo = np.percentile(prof, 95), prof.min()
    dk = (hi - prof) / max(hi - lo, 1e-6)          # 0 = paper, 1 = wedge
    dark = dk > 0.5
    a = th[dark]
    mean = math.degrees(math.atan2(np.sin(np.radians(a)).mean(), np.cos(np.radians(a)).mean()))
    # motion smears the wedge's edges: the soft-edge width grows with the smear
    smear_deg = max(0.0, ((dk > 0.15).mean() - (dk > 0.85).mean()) * 360 / 1.4 - 0.5)
    theta0 = mean - INDEX_DEG / 2
    to_px = make_mapper(center, axes, ang, theta0)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)

    def patch(r, a_deg, half_r, half_a):
        # mean Lab over a small grid in the middle of a cell (avoids the outline and pen edges)
        rr, aa = np.meshgrid(np.linspace(r - half_r, r + half_r, 4), np.linspace(a_deg - half_a, a_deg + half_a, 4))
        xs, ys = to_px(rr.ravel(), aa.ravel())
        return sample(lab, xs, ys).mean(0), (float(np.mean(xs)), float(np.mean(ys)))

    codes = [p["code"] for p in keyd["pens"]] + ["."]
    k = len(keyd["cal"])
    cal_vals = {c: [] for c in codes}
    for i, c in enumerate(keyd["cal"]):
        v, _ = patch((CAL_IN + CAL_OUT) / 2, (i + 0.5) * 360 / k, 1.5, 360 / k * 0.25)
        cal_vals[c].append(v)
    cent = np.stack([np.mean(cal_vals[c], 0) for c in codes])
    got, pts, margins = [], [], []
    cell = keyd["cell_mm"]
    for rg in keyd["rings"]:
        rc = (rg["r0"] + rg["r1"]) / 2
        for j in range(rg["n"]):
            v, p = patch(rc, (j + 0.5) * 360 / rg["n"], cell * 0.2, 360 / rg["n"] * 0.2)
            dist = np.sqrt(((cent - v) ** 2).sum(1))
            o = np.argsort(dist)
            got.append(codes[o[0]]); pts.append(p); margins.append(dist[o[1]] - dist[o[0]])
    blur_mm = math.radians(smear_deg) * (INDEX_IN + INDEX_OUT) / 2
    return dict(got=got, pts=pts, margins=np.array(margins), smear_mm=blur_mm, px_per_mm=px_per_mm,
                bgr=bgr, cent=cent, codes=codes)


def analyze(photos, keyfile, rpm, log, note):
    keyd = json.loads(Path(keyfile).read_text())
    truth = keyd["cells"]
    rows = []
    for ph in photos:
        try:
            r = read_disc(ph, keyd)
        except SystemExit as e:
            print(f"{ph}: {e}")
            rows.append([time.strftime("%Y-%m-%d"), Path(ph).name, rpm, "", "", "", "", "", "disc not found; " + note])
            continue
        ok = np.array([g == t for g, t in zip(r["got"], truth)])
        acc = ok.mean() * 100
        conf = {}
        for g, t in zip(r["got"], truth):
            if g != t:
                conf[f"{t}->{g}"] = conf.get(f"{t}->{g}", 0) + 1
        worst = ", ".join(f"{k} x{v}" for k, v in sorted(conf.items(), key=lambda kv: -kv[1])[:3]) or "none"
        print(f"{Path(ph).name}: {acc:5.1f}% of {len(truth)} cells right · smear {r['smear_mm']:.1f} mm "
              f"· {r['px_per_mm']:.1f} px/mm · weakest margin {np.percentile(r['margins'], 5):.1f} · mix-ups: {worst}")
        diag = r["bgr"].copy()
        lw = max(2, diag.shape[1] // 500)
        for (x, y), good in zip(r["pts"], ok):
            col = (0, 200, 0) if good else (0, 0, 255)
            cv2.circle(diag, (int(x), int(y)), lw * 3, col, lw)
        cv2.imwrite(str(Path(ph).with_name(Path(ph).stem + "_diag.jpg")), diag)
        rows.append([time.strftime("%Y-%m-%d"), Path(ph).name, rpm, f"{acc:.1f}", len(truth), int((~ok).sum()),
                     f"{r['smear_mm']:.2f}", f"{r['px_per_mm']:.2f}", f"{worst}; {note}".strip("; ")])
    if log:
        new = not Path(log).exists() or Path(log).stat().st_size == 0
        with open(log, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["date", "photo", "rpm", "accuracy_pct", "cells", "wrong", "smear_mm", "px_per_mm", "notes"])
            w.writerows(rows)
        print(f"logged {len(rows)} row(s) to {log}")


# ------------------------------------------------------------------ simulate
def coloured(template_png, keyd):
    """Paint the template the way a careful person with pens would."""
    pens = {p["code"]: KNOWN.get(p["name"], (128, 128, 128)) for p in keyd["pens"]}
    img = Image.open(template_png).convert("RGB")
    d = ImageDraw.Draw(img)
    px = PAGE_DPI / 25.4
    W = img.size[0]
    cx, cy = W / 2, 0.45 * PAGE_DPI + DISC_R * px
    rng = np.random.default_rng(3)

    def fill(r0, r1, a0, a1, c):
        if c == ".":
            return
        jitter = lambda v: tuple(int(np.clip(x + rng.normal(0, 8), 0, 255)) for x in v)
        angs = np.linspace(math.radians(a0 + 0.6), math.radians(a1 - 0.6), 12)
        pts = [(cx + (r1 - 0.4) * px * math.cos(a), cy - (r1 - 0.4) * px * math.sin(a)) for a in angs]
        pts += [(cx + (r0 + 0.4) * px * math.cos(a), cy - (r0 + 0.4) * px * math.sin(a)) for a in angs[::-1]]
        d.polygon(pts, fill=jitter(pens[c]))

    k = len(keyd["cal"])
    for i, c in enumerate(keyd["cal"]):
        fill(CAL_IN, CAL_OUT, i * 360 / k, (i + 1) * 360 / k, c)
    i = 0
    for rg in keyd["rings"]:
        for j in range(rg["n"]):
            fill(rg["r0"], rg["r1"], j * 360 / rg["n"], (j + 1) * 360 / rg["n"], keyd["cells"][i]); i += 1
    s = int(2 * DISC_R * px) + 4
    return img.crop((int(cx - s / 2), int(cy - s / 2), int(cx + s / 2), int(cy + s / 2)))


def photo_of(disc, out, rot, smear_deg=0.0, seed=1):
    rng = np.random.default_rng(seed)
    src = cv2.cvtColor(np.array(disc), cv2.COLOR_RGB2BGR).astype(np.float32)
    W, H = 1600, 1200
    s = 1050 / src.shape[0]
    acc = np.zeros((H, W, 3), np.float32)
    steps = max(1, int(smear_deg * 2))
    for i in range(steps):
        a = rot + (smear_deg * i / max(1, steps - 1) if steps > 1 else 0)
        M = cv2.getRotationMatrix2D((src.shape[1] / 2, src.shape[0] / 2), a, s)
        M[0, 0] *= 0.97; M[0, 1] *= 0.97
        M[:, 2] += [W / 2 - src.shape[1] / 2, H / 2 - src.shape[0] / 2]
        acc += cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_AREA, borderValue=(70, 70, 70))
    img = cv2.GaussianBlur(acc / steps, (0, 0), 1.2)
    img = img * np.array([0.93, 1.0, 1.06]) * 0.95 + rng.normal(0, 6, img.shape)
    cv2.imwrite(str(out), np.clip(img, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 85])


def simulate():
    template(["black", "blue", "red", "green"], 10.0, 7, "pen_disc.png")
    keyd = json.loads(Path("pen_disc_key.json").read_text())
    disc = coloured("pen_disc.png", keyd)
    # 33 rpm = 200 deg/s. Auto exposure indoors ~1/30 s smears ~6.7 deg; 1/500 s ~0.4 deg.
    for name, smear in [("sim_still.jpg", 0), ("sim_33rpm_1-500s.jpg", 0.4), ("sim_33rpm_1-100s.jpg", 2.0), ("sim_33rpm_1-30s.jpg", 6.7)]:
        photo_of(disc, name, rot=37, smear_deg=smear)
    analyze(["sim_still.jpg", "sim_33rpm_1-500s.jpg", "sim_33rpm_1-100s.jpg", "sim_33rpm_1-30s.jpg"],
            "pen_disc_key.json", "sim", None, "simulated")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("template")
    t.add_argument("--pens", default="black,blue,red,green", help="comma list of your pen colours")
    t.add_argument("--cell", type=float, default=10.0, help="cell size in mm (10 = ~100 cells, 8 = ~170)")
    t.add_argument("--seed", type=int, default=7)
    t.add_argument("-o", default="pen_disc.png")
    t.add_argument("--filled", action="store_true", help="print the colours instead of letters (no pens needed)")
    a_ = sub.add_parser("analyze")
    a_.add_argument("photos", nargs="+")
    a_.add_argument("--key", default="pen_disc_key.json")
    a_.add_argument("--rpm", default="0")
    a_.add_argument("--log")
    a_.add_argument("--note", default="")
    sub.add_parser("simulate")
    a = ap.parse_args()
    if a.cmd == "template":
        template([p.strip().lower() for p in a.pens.split(",") if p.strip()], a.cell, a.seed, a.o, a.filled)
    elif a.cmd == "analyze":
        analyze(a.photos, a.key, a.rpm, a.log, a.note)
    else:
        simulate()


if __name__ == "__main__":
    main()
