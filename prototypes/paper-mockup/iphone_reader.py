#!/usr/bin/env python3
"""Live AURORA reader using any camera the Mac sees, including an iPhone via Continuity Camera.

  python iphone_reader.py                 # opens camera 0; press C to cycle cameras
  python iphone_reader.py --camera 1
  python iphone_reader.py --image photo.jpg   # test without a camera

Keys (click the video window first):
  SPACE  read the current frame
  R      auto-read once a second (for the spinning turntable)
  P      play the last tune again
  M      mode: data disc (decodes the message) / colour test disc (scores cells)
  C      next camera        S  save the current frame        Q  quit

iPhone setup: macOS 13+ and iOS 16+, same Apple ID, Wi-Fi and Bluetooth on. Mount the
phone 15-25 cm above the platter, pointing straight down. The iPhone appears as a camera
(often index 1 or 2; press C until you see its picture).
"""
import argparse, json, subprocess, sys, tempfile, time
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import aurora_mock, pen_test, tune  # noqa: E402

KEY = HERE / "print-kit" / "colour_disc_key.json"
LAST_PLAYED = None
WIN = "AURORA reader  (SPACE read · R auto · P replay · M mode · C camera · S save · Q quit)"


def camera_names():
    """macOS only: camera names, in the order AVFoundation usually lists them."""
    try:
        out = subprocess.run(["system_profiler", "SPCameraDataType"], capture_output=True, text=True, timeout=10).stdout
        return [l.strip().rstrip(":") for l in out.splitlines() if l.startswith("    ") and l.strip().endswith(":")]
    except Exception:
        return []


def open_cam(i):
    cap = cv2.VideoCapture(i)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    return cap if cap.isOpened() else None


def quick_disc(frame):
    """Find the disc on a small copy, fast enough for the live preview."""
    s = 640 / frame.shape[1]
    small = cv2.resize(frame, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    try:
        (x, y), (a, b), ang = aurora_mock.find_disc(cv2.cvtColor(small, cv2.COLOR_BGR2RGB))
        return (x / s, y / s), (a / s, b / s), ang
    except SystemExit:
        return None


def read_frame(frame, mode):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "frame.jpg"
        cv2.imwrite(str(p), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        try:
            if mode == "data":
                name, payload, _ = aurora_mock.decode(p, Path(td) / "out", verbose=False)
                if tune.is_tune(payload):
                    global LAST_PLAYED
                    meta, voices = tune.parse(payload.decode("utf-8", errors="replace"))
                    if payload != LAST_PLAYED:          # play each new disc once, not on every auto read
                        LAST_PLAYED = payload
                        tune.play(tune.synth(meta, voices), block=False)
                    return True, f"PLAYING '{meta.get('title', 'tune')}' · {meta.get('msg', '')[:70]}"
                text = payload.decode("utf-8", errors="replace").strip().replace("\n", " ")
                return True, f"DECODED {len(payload)} B: {text[:90]}{'...' if len(text) > 90 else ''}"
            keyd = json.loads(KEY.read_text())
            r = pen_test.read_disc(p, keyd)
            ok = np.mean([g == t for g, t in zip(r["got"], keyd["cells"])]) * 100
            return ok > 99.9, f"{ok:.1f}% of {len(keyd['cells'])} cells right · smear {r['smear_mm']:.1f} mm"
        except SystemExit as e:
            return False, f"no read: {str(e)[:90]}"
        except Exception as e:  # keep the live view running whatever happens
            return False, f"no read: {type(e).__name__}: {str(e)[:80]}"


def banner(img, lines, ok=None):
    h = 34 * len(lines) + 16
    cv2.rectangle(img, (0, 0), (img.shape[1], h), (20, 20, 24), -1)
    for i, t in enumerate(lines):
        col = (255, 255, 255) if i else ((90, 220, 120) if ok else (90, 120, 255) if ok is False else (230, 230, 230))
        cv2.putText(img, t, (14, 34 + 34 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.8, col, 2, cv2.LINE_AA)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--image", help="use a still image instead of a camera (testing)")
    ap.add_argument("--mode", choices=["data", "colour"], default="data")
    a = ap.parse_args()

    names = camera_names()
    if names:
        print("Cameras found:", ", ".join(f"{i}: {n}" for i, n in enumerate(names)))
    cam_i, cap = a.camera, None
    still = cv2.imread(a.image) if a.image else None
    if still is None:
        cap = open_cam(cam_i)
        if cap is None:
            sys.exit(f"Cannot open camera {cam_i}. Allow camera access for Terminal in "
                     "System Settings > Privacy & Security > Camera, then try again.")
    mode, auto, last_auto, msg, ok, n_ok, n_try = a.mode, False, 0.0, "Press SPACE to read", None, 0, 0
    found, frame_no = None, 0
    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WIN, 1200, 700)
    while True:
        if still is not None:
            frame = still.copy()
        else:
            got, frame = cap.read()
            if not got:
                frame = np.zeros((720, 1280, 3), np.uint8)
        frame_no += 1
        if frame_no % 5 == 1:
            found = quick_disc(frame)
        view = frame.copy()
        if found:
            (cx, cy), (ax, bx), ang = found
            cv2.ellipse(view, ((cx, cy), (2 * ax, 2 * bx), ang), (80, 220, 120), 3)
        do_read = False
        k = cv2.waitKey(1) & 0xFF
        if k in (ord("q"), 27):
            break
        if k == ord(" "):
            do_read = True
        if k == ord("r"):
            auto, n_ok, n_try = not auto, 0, 0
        if k == ord("p") and LAST_PLAYED:
            meta, voices = tune.parse(LAST_PLAYED.decode("utf-8", errors="replace"))
            tune.play(tune.synth(meta, voices), block=False)
        if k == ord("m"):
            mode = "colour" if mode == "data" else "data"
            msg, ok = f"mode: {mode} disc", None
        if k == ord("s"):
            out = HERE / "shots"; out.mkdir(exist_ok=True)
            f = out / time.strftime("iphone_%Y%m%d_%H%M%S.jpg"); cv2.imwrite(str(f), frame)
            msg, ok = f"saved {f.name}", None
        if k == ord("c") and still is None:
            cap.release()
            for _ in range(6):
                cam_i = (cam_i + 1) % 6
                cap = open_cam(cam_i)
                if cap:
                    break
            nm = names[cam_i] if cam_i < len(names) else ""
            msg, ok = f"camera {cam_i} {nm}", None
        if auto and time.time() - last_auto > 1.0:
            do_read, last_auto = True, time.time()
        if do_read:
            ok, msg = read_frame(frame, mode)
            if auto:
                n_try += 1; n_ok += int(ok)
        lines = [msg, f"mode: {mode} disc  ·  camera {cam_i}  ·  disc {'found' if found else 'not found'}"
                      + (f"  ·  auto: {n_ok}/{n_try} reads OK" if auto else "")]
        banner(view, lines, ok)
        cv2.imshow(WIN, view)
    if cap:
        cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
