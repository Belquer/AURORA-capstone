#!/usr/bin/env python3
"""Grab still frames for the Phase 0 mockup.

  ESP32-CAM / ESP32 + Arducam running the CameraWebServer sketch:
      python capture.py esp32 192.168.1.50 -n 5
  Lock a short exposure on the ESP32 for spinning tests (0-1200, lower = shorter; needs bright light):
      python capture.py esp32 192.168.1.50 -n 5 --exposure 20
  Back to automatic exposure:
      python capture.py esp32 192.168.1.50 -n 1 --auto
  USB camera (Arducam USB, webcam):
      python capture.py usb 0 -n 5

Frames are saved as shots/YYYYmmdd_HHMMSS_<n>.jpg. Use --decode to run the
decoder on each frame right away.
"""
import argparse, pathlib, subprocess, sys, time, urllib.request

import cv2
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent


def esp32_set(ip, var, val):
    # CameraWebServer settings endpoint
    urllib.request.urlopen(f"http://{ip}/control?var={var}&val={val}", timeout=5).read()


def grab_esp32(ip):
    # CameraWebServer exposes a single JPEG at /capture.
    with urllib.request.urlopen(f"http://{ip}/capture", timeout=10) as r:
        buf = np.frombuffer(r.read(), np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError("ESP32 returned something that is not a JPEG")
    return img


def open_usb(index):
    cap = cv2.VideoCapture(int(index))
    # Ask for the largest frame the camera offers; it falls back if unsupported.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 4000)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 3000)
    if not cap.isOpened():
        raise RuntimeError(f"No USB camera at index {index}")
    for _ in range(10):          # let auto exposure settle
        cap.read()
    return cap


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", choices=["esp32", "usb"])
    ap.add_argument("where", help="ESP32 IP address, or USB camera index")
    ap.add_argument("-n", type=int, default=1, help="number of frames")
    ap.add_argument("--gap", type=float, default=0.5, help="seconds between frames")
    ap.add_argument("--out", default="shots")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--exposure", type=int, help="ESP32: manual exposure 0-1200 (turns auto exposure off)")
    ap.add_argument("--auto", action="store_true", help="ESP32: back to automatic exposure")
    a = ap.parse_args()

    out = pathlib.Path(a.out); out.mkdir(exist_ok=True)
    cap = open_usb(a.where) if a.source == "usb" else None
    if a.source == "esp32":
        esp32_set(a.where, "framesize", 13)          # UXGA 1600 x 1200
        if a.exposure is not None:
            esp32_set(a.where, "aec", 0); esp32_set(a.where, "aec_value", a.exposure)
        elif a.auto:
            esp32_set(a.where, "aec", 1)
        time.sleep(0.5)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    for i in range(a.n):
        if cap is not None:
            ok, img = cap.read()
            if not ok:
                sys.exit("USB camera stopped returning frames")
        else:
            img = grab_esp32(a.where)
        p = out / f"{stamp}_{i}.jpg"
        cv2.imwrite(str(p), img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        print(f"{p}  {img.shape[1]}x{img.shape[0]}")
        if a.decode:
            subprocess.run([sys.executable, str(HERE / "aurora_mock.py"), "decode", str(p),
                            "-o", str(out / f"{stamp}_{i}_decoded")])
        time.sleep(a.gap)
    if cap is not None:
        cap.release()


if __name__ == "__main__":
    main()
