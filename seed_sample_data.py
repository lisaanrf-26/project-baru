import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "tasks.db"

UPLOAD_FOLDER.mkdir(exist_ok=True)

def generate_sample_image(filename, title, officer, role_color=(37, 99, 235)):
    # Buat gambar simulasi foto berukuran 1280x720
    img = Image.new('RGB', (1280, 720), color=(15, 23, 42))
    draw = ImageDraw.Draw(img)

    # Gradient-like background pattern
    for y in range(0, 720, 20):
        color = (15 + int(y * 0.03), 23 + int(y * 0.05), 42 + int(y * 0.08))
        draw.rectangle([0, y, 1280, y + 20], fill=color)

    # Border & frame
    draw.rectangle([40, 40, 1240, 680], outline=role_color, width=4)

    # Simbol kamera / ikon
    draw.ellipse([580, 220, 700, 340], fill=role_color)
    draw.rectangle([540, 260, 740, 400], fill=role_color)
    draw.ellipse([610, 300, 670, 360], fill=(255, 255, 255))

    # Teks Dokumentasi
    # Default Pillow font
    draw.text((640, 460), title, fill=(255, 255, 255), anchor="mm")
    draw.text((640, 500), f"Petugas: {officer}", fill=(203, 213, 225), anchor="mm")

    # Watermark stempel waktu
    now_str = datetime.now().strftime("%d %b %Y • %H:%M WIB")
    draw.rectangle([850, 600, 1220, 660], fill=(0, 0, 0, 180), outline=(255, 255, 255))
    draw.text((870, 615), f"SiTugas Bukti Lapangan", fill=(56, 189, 248))
    draw.text((870, 635), f"{now_str} • {officer}", fill=(255, 255, 255))

    out_path = UPLOAD_FOLDER / filename
    img.save(out_path, format="WEBP", quality=75)
    return out_path.stat().st_size

from app import init_db

def seed():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Periksa apakah sudah ada data
    cursor.execute("SELECT COUNT(*) FROM support_tasks")
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"Database sudah memiliki {count} data tugas. Melewatkan seeding.")
        conn.close()
        return

    now = datetime.now()

    samples = [
      {
          "role": "satpam",
          "task_title": "Patroli Rutin Titik Pantau Gerbang Barat & Pagar Keliling",
          "officer_name": "Sertu Budi Santoso",
          "shift": "Shift 1 (Pagi 07:00-15:00)",
          "location": "Pos Gerbang Barat & Area Parkir Timur",
          "status": "selesai",
          "description": "Pemeriksaan 8 titik barcode patroli. Pagar kawat dan kunci gembok dalam keadaan baik dan aman terkendali.",
          "orig_size": 4850230,  # ~4.85 MB kamera mentah
          "time_offset_min": -65,
          "color": (37, 99, 235)
      },
      {
          "role": "cleaning",
          "task_title": "Pembersihan Menyeluruh & Sanitasi Toilet Lantai 2",
          "officer_name": "Siti Rahmawati",
          "shift": "Shift 1 (Pagi 07:00-15:00)",
          "location": "Toilet Pria & Wanita Lt. 2",
          "status": "selesai",
          "description": "Pembersihan kloset, wastafel, pel lantai dengan wangi lavender. Sabun cuci tangan dan tisu roll telah diisi ulang penuh.",
          "orig_size": 5210400,  # ~5.21 MB
          "time_offset_min": -130,
          "color": (5, 150, 105)
      },
      {
          "role": "teknisi",
          "task_title": "Pemanasan Rutin Genset & Cek Level Solar Cadangan",
          "officer_name": "Agus Setiawan",
          "shift": "Non-Shift / Reguler",
          "location": "Ruang Power House / Genset Utama",
          "status": "selesai",
          "description": "Uji jalan genset selama 20 menit beban normal. Tegangan 380V stabil, oli aman, solar tangki harian terisi 85%.",
          "orig_size": 6120000,  # ~6.12 MB
          "time_offset_min": -240,
          "color": (217, 119, 6)
      },
      {
          "role": "satpam",
          "task_title": "Pemeriksaan Tamu & Kendaraan Truk Ekspedisi Masuk",
          "officer_name": "Ahmad Dani",
          "shift": "Shift 1 (Pagi 07:00-15:00)",
          "location": "Pos Gerbang Utama",
          "status": "selesai",
          "description": "Pemeriksaan surat jalan dan identitas supir ekspedisi logistik. Diberikan badge visitor dan kartu parkir resmi.",
          "orig_size": 3900120,  # ~3.9 MB
          "time_offset_min": -320,
          "color": (37, 99, 235)
      }
    ]

    for item in samples:
        task_id = uuid.uuid4().hex
        task_dt = now + timedelta(minutes=item["time_offset_min"])
        task_time_str = task_dt.strftime("%Y-%m-%dT%H:%M")
        created_at_str = task_dt.strftime("%Y-%m-%d %H:%M:%S")
        img_filename = f"sample_{task_id[:10]}.webp"

        comp_size = generate_sample_image(img_filename, item["task_title"], item["officer_name"], item["color"])

        cursor.execute("""
            INSERT INTO support_tasks (
                id, role, task_title, officer_name, shift, location,
                status, description, original_size, compressed_size,
                image_filename, task_time, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id, item["role"], item["task_title"], item["officer_name"],
            item["shift"], item["location"], item["status"], item["description"],
            item["orig_size"], comp_size, img_filename, task_time_str, created_at_str
        ))

    conn.commit()
    conn.close()
    print("[OK] Berhasil memasukkan sample data tugas pendukung (Satpam, Cleaning, Teknisi)!")

if __name__ == "__main__":
    seed()
