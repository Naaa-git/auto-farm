# Miscrits AutoFarm - Setup Guide (Windows)

## 1. Install Python
Download Python 3.11+ dari https://python.org
Centang **"Add Python to PATH"** saat install.

## 2. Install Tesseract OCR
Download installer: https://github.com/UB-Mannheim/tesseract/wiki
Install ke default path: `C:\Program Files\Tesseract-OCR\`

Kalau path berbeda, uncomment dan edit baris ini di `screen_reader.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

## 3. Install dependencies
Buka CMD / PowerShell di folder autofarm:
```
pip install -r requirements.txt
pip install keyboard
```

## 4. Screenshot assets game
Buat folder `assets/` lalu screenshot bagian-bagian UI game:

| File | Isi screenshot |
|------|----------------|
| `assets/attack_btn.png` | Tombol attack/skill yang akan di-spam |
| `assets/capture_btn.png` | Tombol capture |
| `assets/battle_start.png` | Bagian UI yang **hanya muncul saat battle** (misalnya HP bar atau nama musuh) |

> Tips: Pakai Snipping Tool (Win+Shift+S), crop sekecil mungkin tapi cukup unik.

## 5. Kalibrasi region OCR
Jalankan calibration tool:
```
python calibrate.py
```

Gunakan menu:
1. **Track mouse** → hover ke area nama creature, catat X Y
2. **Screenshot region** → cek apakah region sudah benar
3. **Test OCR creature name** → pastikan nama terbaca
4. **Test OCR capture %** → pastikan angka % terbaca
5. **Save** → simpan ke config.json

## 6. Edit config.json
Sesuaikan:
- `capture_list`: tambah nama creature dengan mode `"manual"` atau `"auto"`
- `keys.attack`: tombol skill yang dipakai (default `"1"`)
- `capture_threshold`: minimum capture % sebelum bot mencoba capture (default `80`)

## 7. Jalankan bot
```
python main.py
```

- **F10** = Start / Pause / Resume
- **F12** = Stop total

## Troubleshooting

**OCR tidak akurat** → Coba adjust region di calibrate.py, pastikan teks di layar cukup besar dan kontras

**Battle tidak terdeteksi** → Pastikan `assets/battle_start.png` hanya muncul saat battle, bukan di menu utama

**Bot klik terlalu cepat/lambat** → Sesuaikan nilai `timing` di config.json
