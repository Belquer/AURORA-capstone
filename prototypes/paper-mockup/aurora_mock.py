#!/usr/bin/env python3
"""AURORA paper mockup reader: photograph a printed paper disc, get the file back.

This is a SCALED-UP mockup: 2 mm cells instead of 25 um, so an ordinary inkjet or laser
printer and a cheap camera (Arducam / ESP32-CAM OV2640, a phone) are enough. The pipeline
reads: photo -> unwrap -> classify colors -> error correction -> bytes.

  python aurora_mock.py decode photo.jpg              # -> recovered file + report
  python aurora_mock.py capacity

Encoding (making print files) is private. Ready-to-print discs are in print-kit/.

Requires: numpy, opencv-python, pillow, reedsolo
"""
import argparse, math, struct, sys, zlib
from pathlib import Path

import cv2
import numpy as np
from reedsolo import RSCodec, ReedSolomonError

# ---------------------------------------------------------------- geometry (mm)
DISC_R = 88.9          # 7-inch disc
EDGE_IN, EDGE_OUT = 81.5, 84.0     # solid black ring the decoder finds the disc by; 5 mm white margin outside it
INDEX_IN, INDEX_OUT = 78.0, 80.5   # index ring: one black wedge marks angle 0
INDEX_DEG = 10.0
CAL_IN, CAL_OUT = 31.0, 35.0       # calibration ring: the 8 colors, 4 times round
CAL_REPEAT = 4
CELL = 2.0                          # cell size (mm), radial and tangential
DATA_IN, DATA_OUT = 36.0, 76.0
HOLE_R = 3.6                        # spindle hole (7.2 mm)
DPI = 600
NSYM = 32                           # Reed-Solomon parity bytes per 255-byte block
MAGIC = b"AUR1"

# 3 bits per cell: bit2 = cyan, bit1 = magenta, bit0 = yellow. Printed on white paper,
# cyan absorbs red, magenta absorbs green, yellow absorbs blue.
def state_rgb(v):
    c, m, y = (v >> 2) & 1, (v >> 1) & 1, v & 1
    return (255 * (1 - c), 255 * (1 - m), 255 * (1 - y))


def rings():
    """Center radius and cell count of every data ring, inside to outside."""
    out, r = [], DATA_IN + CELL / 2
    while r + CELL / 2 <= DATA_OUT + 1e-9:
        out.append((r, int(2 * math.pi * r // CELL)))
        r += CELL
    return out


def capacity_cells():
    return sum(n for _, n in rings())


# ---------------------------------------------------------------- framing
def capacity_bytes():
    return capacity_cells() * 3 // 8


def max_body(cap):
    """Largest body whose Reed-Solomon encoding fits in cap bytes."""
    full, rest = divmod(cap, 255)
    return full * (255 - NSYM) + max(0, rest - NSYM)


def scramble(b: bytes) -> bytes:
    """XOR with a fixed pseudo-random stream, so padding and repeated bytes still give an
    even mix of colours (a long run of zeros would otherwise print as blank cells).
    Applying it twice undoes it."""
    ks = np.random.default_rng(20261014).integers(0, 256, len(b), dtype=np.uint8)
    return (np.frombuffer(b, np.uint8) ^ ks).tobytes()


def unframe(raw: bytes):
    dec = RSCodec(NSYM).decode(scramble(raw))[0]
    if dec[:4] != MAGIC:
        raise ValueError("no AURORA header")
    ln, nl = struct.unpack(">IB", dec[4:9])
    nm = dec[9:9 + nl].decode(errors="replace")
    payload = bytes(dec[9 + nl:9 + nl + ln])
    end = 9 + nl + ln
    if struct.unpack(">I", dec[end:end + 4])[0] != zlib.crc32(bytes(dec[:end])):
        raise ValueError("CRC mismatch")
    return nm, payload


def states_to_bytes(st):
    bits = np.stack([(st >> 2) & 1, (st >> 1) & 1, st & 1], 1).reshape(-1).astype(np.uint8)
    return np.packbits(bits[: len(bits) // 8 * 8]).tobytes()


# ---------------------------------------------------------------- encode
def find_disc(rgb):
    """Fit the black ring. Returns center, semi-axes (px for EDGE_OUT) and ellipse angle."""
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    g = cv2.GaussianBlur(g, (5, 5), 0)
    _, dark = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # RETR_LIST, not EXTERNAL: the ring may sit inside another dark outline (a mat, a cut line)
    cnts, _ = cv2.findContours(dark, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    H, W = dark.shape
    mid = (EDGE_IN + EDGE_OUT) / 2 / EDGE_OUT          # the ring's centre line, as a fraction of its outer edge
    best = None
    for cnt in cnts:
        if len(cnt) < 50:
            continue
        x0, y0, w0, h0 = cv2.boundingRect(cnt)
        if x0 <= 1 or y0 <= 1 or x0 + w0 >= W - 1 or y0 + h0 >= H - 1:
            continue                      # touches the frame: table, mat or shadow, not the disc
        area = cv2.contourArea(cnt)
        (x, y), (w, h), ang = cv2.fitEllipse(cnt)
        if not (0.85 < area / (math.pi * w * h / 4 + 1e-9) < 1.1 and min(w, h) / max(w, h) > 0.6):
            continue
        # confirm it is THE ring: dark all the way round along its centre line
        t = np.linspace(0, 2 * math.pi, 180, endpoint=False)
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        u, v = mid * w / 2 * np.cos(t), mid * h / 2 * np.sin(t)
        xs = np.clip((x + u * ca - v * sa).astype(int), 0, W - 1)
        ys = np.clip((y + u * sa + v * ca).astype(int), 0, H - 1)
        if (dark[ys, xs] > 0).mean() < 0.9:
            continue
        if best is None or area > best[0]:
            best = (area, (x, y), (w / 2, h / 2), ang)
    if best is None:
        raise SystemExit("could not find the disc's black ring; is the whole disc in frame and evenly lit?")
    return best[1:]


def make_mapper(center, axes, ang_deg, theta0):
    cx, cy = center
    a, b = axes
    ca, sa = math.cos(math.radians(ang_deg)), math.sin(math.radians(ang_deg))

    def to_px(r_mm, th_deg):
        th = np.radians(np.asarray(th_deg) + theta0)
        u = (np.asarray(r_mm) / EDGE_OUT) * a * np.cos(th)
        v = -(np.asarray(r_mm) / EDGE_OUT) * b * np.sin(th)
        return cx + u * ca - v * sa, cy + u * sa + v * ca
    return to_px


def sample(img, xs, ys):
    xs = np.asarray(xs, np.float32).reshape(1, -1)
    ys = np.asarray(ys, np.float32).reshape(1, -1)
    return cv2.remap(img, xs, ys, cv2.INTER_LINEAR)[0].astype(np.float32)


def read_cells(photo: Path):
    """Photo -> (cell states, diagnostics)."""
    bgr = cv2.imread(str(photo))
    if bgr is None:
        raise SystemExit(f"cannot read {photo}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    center, axes, ang = find_disc(rgb)
    px_per_mm = (axes[0] + axes[1]) / 2 / EDGE_OUT
    k = max(1, int(px_per_mm * CELL * 0.35)) | 1
    soft = cv2.blur(rgb, (k, k))
    gray = cv2.cvtColor(soft, cv2.COLOR_RGB2GRAY)

    # angle 0: the dark wedge in the index ring
    m0 = make_mapper(center, axes, ang, 0.0)
    th = np.arange(0, 360, 0.25)
    x, y = m0(np.full_like(th, (INDEX_IN + INDEX_OUT) / 2), th)
    prof = sample(gray, x, y)
    dark = prof < (prof.max() + prof.min()) / 2
    # center of the circular dark run, then back off half the wedge
    ang_dark = th[dark]
    mean = math.degrees(math.atan2(np.sin(np.radians(ang_dark)).mean(), np.cos(np.radians(ang_dark)).mean()))
    theta0 = mean - INDEX_DEG / 2
    to_px = make_mapper(center, axes, ang, theta0)

    # color calibration: class centroids from the calibration ring
    kk = 8 * CAL_REPEAT
    cal_th = (np.arange(kk) + 0.5) * 360 / kk
    x, y = to_px(np.full(kk, (CAL_IN + CAL_OUT) / 2), cal_th)
    cal = sample(soft, x, y)
    cent = np.stack([cal[np.arange(kk) % 8 == s].mean(0) for s in range(8)])

    # data cells
    rs, ths = [], []
    for r, n in rings():
        rs += [r] * n
        ths += list((np.arange(n) + 0.5) * 360 / n)
    x, y = to_px(np.array(rs), np.array(ths))
    vals = sample(soft, x, y)
    d2 = ((vals[:, None, :] - cent[None]) ** 2).sum(2)
    states = d2.argmin(1)
    srt = np.sort(d2, 1)
    margin = (np.sqrt(srt[:, 1]) - np.sqrt(srt[:, 0]))
    diag = dict(center=center, px_per_mm=px_per_mm, theta0=theta0, margin=margin, cent=cent,
                bgr=bgr, ellipse=(center, axes, ang), pts=(x, y), index_xy=to_px(np.array([INDEX_OUT + 2.0]), np.array([0.0])))
    return states, diag


def write_diag(diag, states, path: Path):
    """Photo with the found edge ellipse, angle-zero mark and every sampling point."""
    img = diag["bgr"].copy()
    (cx, cy), (a, b), ang = diag["ellipse"]
    lw = max(1, img.shape[1] // 800)
    cv2.ellipse(img, ((float(cx), float(cy)), (2 * float(a), 2 * float(b)), float(ang)), (0, 255, 0), lw)
    ix, iy = diag["index_xy"]
    cv2.line(img, (int(cx), int(cy)), (int(ix[0]), int(iy[0])), (0, 0, 255), lw)
    weak = diag["margin"] < np.percentile(diag["margin"], 2)
    for xi, yi, w in zip(*diag["pts"], weak):
        cv2.circle(img, (int(xi), int(yi)), lw + 1, (0, 0, 255) if w else (0, 0, 0), -1)
    cv2.imwrite(str(path), img)


def decode(photo: Path, outdir: Path, verbose=True):
    states, diag = read_cells(photo)
    center, px_per_mm, theta0, margin = diag["center"], diag["px_per_mm"], diag["theta0"], diag["margin"]
    raw = states_to_bytes(states)

    name, payload, why = None, None, ""
    try:
        name, payload = unframe(raw[: capacity_bytes()])
    except (ReedSolomonError, ValueError) as e:
        why = str(e)
    outdir.mkdir(parents=True, exist_ok=True)
    write_diag(diag, states, outdir / "diag.png")
    if verbose:
        print(f"disc found: center ({center[0]:.0f}, {center[1]:.0f}) px, {px_per_mm:.1f} px/mm, "
              f"index at {theta0 % 360:.1f} deg; weakest-cell color margin {np.percentile(margin, 1):.1f}")
    if payload is None:
        raise SystemExit(f"decode FAILED ({why}): too many cell errors for the error correction. "
                         f"Check {outdir / 'diag.png'}")
    dst = outdir / ("decoded_" + Path(name).name)
    dst.write_bytes(payload)
    if verbose:
        print(f"decoded {len(payload)} B -> {dst}")
    return name, payload, states


# ---------------------------------------------------------------- simulate a camera photo
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("decode"); d.add_argument("photo"); d.add_argument("-o", default="decoded")
    sub.add_parser("capacity")
    a = ap.parse_args()
    if a.cmd == "decode":
        decode(Path(a.photo), Path(a.o))
    else:
        n = capacity_cells()
        raw = n * 3 // 8
        print(f"{len(rings())} rings, {n} cells, {raw} B raw, {max_body(raw) - 13} B payload (minus file name)")


if __name__ == "__main__":
    main()
