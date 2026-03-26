"""
Calibration helper — jalankan ini untuk:
1. Cek koordinat mouse kamu
2. Screenshot region tertentu
3. Test OCR nama creature & capture %
4. Test deteksi battle active

Run: python calibrate.py
"""

import time
import json
import pyautogui
import pytesseract
from pathlib import Path
import screen_reader as sr

# Uncomment jika tesseract tidak di PATH:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def track_mouse():
    print("\n[MOUSE TRACKER] Gerakin mouse ke posisi yang kamu mau, tekan Ctrl+C untuk stop.")
    try:
        while True:
            x, y = pyautogui.position()
            print(f"  X: {x:4d}  Y: {y:4d}", end="\r")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nDone.")


def screenshot_region():
    print("\n[SCREENSHOT REGION]")
    print("Masukkan koordinat region (x y w h), pisah spasi:")
    raw = input("  > ").split()
    if len(raw) != 4:
        print("Format salah.")
        return
    region = list(map(int, raw))
    img = sr.screenshot(region)
    out = "calibration_region.png"
    img.save(out)
    print(f"  Saved: {out}")


def test_ocr_creature():
    print("\n[TEST OCR - CREATURE NAME]")
    print("Masukkan region creature name (x y w h):")
    raw = input("  > ").split()
    region = list(map(int, raw))
    print("  Membaca layar...")
    name = sr.read_creature_name(region)
    print(f"  Hasil OCR: '{name}'")


def test_ocr_capture_pct():
    print("\n[TEST OCR - CAPTURE %]")
    print("Masukkan region capture % (x y w h):")
    raw = input("  > ").split()
    region = list(map(int, raw))
    print("  Membaca layar...")
    pct = sr.read_capture_percentage(region)
    print(f"  Hasil OCR: {pct}%")


def save_regions_to_config():
    print("\n[SAVE REGIONS] Masukkan semua region lalu save ke config.json")
    regions = {}
    for name in ["creature_name", "capture_percentage", "battle_indicator"]:
        print(f"  Region '{name}' (x y w h): ", end="")
        raw = input().split()
        regions[name] = list(map(int, raw))

    config_path = Path("config.json")
    with open(config_path) as f:
        cfg = json.load(f)
    cfg["regions"] = regions
    with open(config_path, "w") as f:
        json.dump(cfg, f, indent=2)
    print("  Saved ke config.json!")


MENU = {
    "1": ("Track posisi mouse", track_mouse),
    "2": ("Screenshot region", screenshot_region),
    "3": ("Test OCR creature name", test_ocr_creature),
    "4": ("Test OCR capture %", test_ocr_capture_pct),
    "5": ("Save regions ke config.json", save_regions_to_config),
    "q": ("Keluar", None),
}

if __name__ == "__main__":
    print("=== Miscrits AutoFarm - Calibration Tool ===")
    while True:
        print()
        for key, (label, _) in MENU.items():
            print(f"  [{key}] {label}")
        choice = input("\nPilih: ").strip().lower()
        if choice == "q":
            break
        if choice in MENU and MENU[choice][1]:
            MENU[choice][1]()
        else:
            print("Pilihan tidak valid.")
