#!/usr/bin/env python3
"""Tiny tunes for paper discs: a few hundred bytes of score, synthesised into sound.

A paper disc holds ~1 KB, about one second of real compressed audio. A score fits a whole
tune. Real AURORA discs (~29 MB per side) carry full Opus audio instead.

  python tune.py play print-kit/first_light.tune     # hear it without a disc
  python tune.py wav print-kit/first_light.tune -o out.wav

Format (plain text):
  AURORA tune 1
  title: First light
  msg: any text shown when the disc is read
  bpm: 100
  wave: tri            (sine, tri, square)
  voice1: E5:1 G5:1 C6:2 r:1 ...   note+octave:beats, r = rest
  voice2: C3:4 G2:4 ...
"""
import argparse, platform, shutil, subprocess, sys, tempfile, threading, wave
from pathlib import Path

import numpy as np

SR = 22050
NOTE = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}


def is_tune(data: bytes) -> bool:
    return data.startswith(b"AURORA tune")


def parse(text: str):
    meta, voices = {}, []
    for line in text.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip().lower(), v.strip()
        if k.startswith("voice"):
            notes = []
            for tok in v.split():
                n, beats = tok.split(":")
                notes.append((None if n.lower() == "r" else freq(n), float(beats)))
            voices.append(notes)
        else:
            meta[k] = v
    return meta, voices


def freq(n):
    semis = NOTE[n[0].upper()]
    i = 1
    if len(n) > 2 and n[1] in "#b":
        semis += 1 if n[1] == "#" else -1
        i = 2
    octave = int(n[i:])
    return 440.0 * 2 ** ((semis + 12 * (octave - 4)) / 12)


def synth(meta, voices):
    beat = 60.0 / float(meta.get("bpm", 100))
    wave_kind = meta.get("wave", "tri")
    length = max(sum(b for _, b in v) for v in voices) * beat + 0.5
    out = np.zeros(int(length * SR))
    for vi, notes in enumerate(voices):
        t0 = 0.0
        gain = 0.45 if vi == 0 else 0.3
        for f, beats in notes:
            dur = beats * beat
            if f:
                n = int(dur * SR)
                t = np.arange(n) / SR
                ph = (f * t) % 1.0
                if wave_kind == "sine":
                    w = np.sin(2 * np.pi * ph)
                elif wave_kind == "square":
                    w = np.where(ph < 0.5, 0.6, -0.6)
                else:
                    w = 4 * np.abs(ph - 0.5) - 1
                env = np.minimum(1, t / 0.01) * np.exp(-t * (2.5 if vi == 0 else 1.2))
                env *= np.minimum(1, (dur - t) / 0.03)
                s = int(t0 * SR)
                out[s:s + n] += gain * w * env
            t0 += dur
    return out / max(1e-9, np.abs(out).max()) * 0.8


def write_wav(samples, path):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((samples * 32767).astype(np.int16).tobytes())


def play(samples, block=True):
    """Play through the computer's audio output (macOS afplay, Linux aplay)."""
    tmp = Path(tempfile.gettempdir()) / "aurora_tune.wav"
    write_wav(samples, tmp)
    player = "afplay" if platform.system() == "Darwin" else ("aplay" if shutil.which("aplay") else None)
    if not player:
        print(f"no audio player found; wrote {tmp}")
        return
    run = lambda: subprocess.run([player, str(tmp)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if block:
        run()
    else:
        threading.Thread(target=run, daemon=True).start()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["play", "wav"])
    ap.add_argument("file")
    ap.add_argument("-o", default="tune.wav")
    a = ap.parse_args()
    meta, voices = parse(Path(a.file).read_text())
    s = synth(meta, voices)
    print(f"{meta.get('title', 'tune')}: {len(s) / SR:.1f} s, {Path(a.file).stat().st_size} bytes of score")
    if a.cmd == "wav":
        write_wav(s, a.o); print(f"wrote {a.o}")
    else:
        play(s)


if __name__ == "__main__":
    main()
