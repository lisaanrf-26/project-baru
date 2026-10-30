import os
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
from PIL import Image, ImageOps

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
DB_PATH = BASE_DIR / "tasks.db"

UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # Maksimum upload 32MB

INDONESIAN_DAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
INDONESIAN_MONTHS = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

ROLE_CONFIG = {
    "satpam": {
        "title": "Satpam / Security",
        "icon": "shield-check",
        "color": "blue"
    },
    "cleaning": {
        "title": "Cleaning Service",
        "icon": "sparkles",
        "color": "emerald"
    },
    "teknisi": {
        "title": "Teknisi & Maintenance",
        "icon": "wrench",
        "color": "amber"
    },
    "driver": {
        "title": "Driver / Pengemudi",
        "icon": "truck",
        "color": "indigo"
    },
    "ob": {
        "title": "Pramubakti / OB",
        "icon": "coffee",
        "color": "purple"
    },
    "lainnya": {
        "title": "Petugas Pendukung Lainnya",
        "icon": "clipboard-list",
        "color": "slate"
    }
}

def format_indonesian_datetime(dt_obj):
    day_name = INDONESIAN_DAYS[dt_obj.weekday()]
    month_name = INDONESIAN_MONTHS[dt_obj.month - 1]
    time_str = dt_obj.strftime("%H:%M")
    return f"{day_name}, {dt_obj.day} {month_name} {dt_obj.year} • {time_str} WIB"

def format_size(bytes_num):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_num < 1024.0:
            return f"{bytes_num:.1f} {unit}"
        bytes_num /= 1024.0
    return f"{bytes_num:.1f} TB"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tasks (
            id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            task_title TEXT NOT NULL,
            officer_name TEXT NOT NULL,
            shift TEXT NOT NULL,
            location TEXT NOT NULL,
            status TEXT NOT NULL,
            description TEXT,
            original_size INTEGER NOT NULL,
            compressed_size INTEGER NOT NULL,
            image_filename TEXT NOT NULL,
            task_time TEXT NOT NULL,
            created_at TEXT NOT NULL,
            nip_ppnpn TEXT,
            unit_kerja TEXT
        )
    """)
    cursor.execute("PRAGMA table_info(support_tasks)")
    columns = [col[1] for col in cursor.fetchall()]
    if "nip_ppnpn" not in columns:
        cursor.execute("ALTER TABLE support_tasks ADD COLUMN nip_ppnpn TEXT")
    if "unit_kerja" not in columns:
        cursor.execute("ALTER TABLE support_tasks ADD COLUMN unit_kerja TEXT")
    conn.commit()
    conn.close()

init_db()

def compress_and_save_image(file_storage, max_dim=1440, quality=78):
    """
    Mengompres foto ke format WebP berkualitas optimal.
    Memperbaiki rotasi EXIF dari kamera HP/tablet secara otomatis.
    """
    unique_id = uuid.uuid4().hex[:12]
    out_filename = f"task_{unique_id}.webp"
    out_path = UPLOAD_FOLDER / out_filename

    img = Image.open(file_storage)
    img = ImageOps.exif_transpose(img)

    if img.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'RGBA':
            bg.paste(img, mask=img.split()[3])
        else:
            bg.paste(img.convert('RGB'))
        img = bg
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize cerdas menjaga rasio aspek
    w, h = img.size
    if w > max_dim or h > max_dim:
        if w > h:
            new_w = max_dim
            new_h = int((h * max_dim) / w)
        else:
            new_h = max_dim
            new_w = int((w * max_dim) / h)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    img.save(out_path, format="WEBP", quality=quality, optimize=True)
    compressed_size = out_path.stat().st_size
    return out_filename, compressed_size

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    role_filter = request.args.get("role", "").strip()
    status_filter = request.args.get("status", "").strip()
    search_query = request.args.get("q", "").strip()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = "SELECT * FROM support_tasks WHERE 1=1"
    params = []

    if role_filter and role_filter != "all":
        sql += " AND role = ?"
        params.append(role_filter)

    if status_filter and status_filter != "all":
        sql += " AND status = ?"
        params.append(status_filter)

    if search_query:
        sql += " AND (task_title LIKE ? OR officer_name LIKE ? OR location LIKE ? OR description LIKE ?)"
        term = f"%{search_query}%"
        params.extend([term, term, term, term])

    sql += " ORDER BY task_time DESC, created_at DESC"
    cursor.execute(sql, params)
    rows = cursor.fetchall()

    tasks = []
    for row in rows:
        item = dict(row)
        raw_dt = item.get("task_time") or item.get("created_at")
        try:
            if "T" in raw_dt:
                dt_obj = datetime.fromisoformat(raw_dt)
            else:
                dt_obj = datetime.strptime(raw_dt, "%Y-%m-%d %H:%M:%S")
            item["formatted_datetime"] = format_indonesian_datetime(dt_obj)
            item["day_name"] = INDONESIAN_DAYS[dt_obj.weekday()]
            item["time_str"] = dt_obj.strftime("%H:%M WIB")
            item["date_str"] = f"{dt_obj.day} {INDONESIAN_MONTHS[dt_obj.month - 1]} {dt_obj.year}"
        except Exception:
            item["formatted_datetime"] = raw_dt
            item["day_name"] = ""
            item["time_str"] = ""
            item["date_str"] = raw_dt

        # Persentase hemat memori
        orig = item.get("original_size", 0)
        comp = item.get("compressed_size", 0)
        saved = max(0, orig - comp)
        item["original_size_fmt"] = format_size(orig)
        item["compressed_size_fmt"] = format_size(comp)
        item["saved_bytes_fmt"] = format_size(saved)
        item["saved_percent"] = round((saved / orig * 100), 1) if orig > 0 else 0
        item["nip_ppnpn"] = item.get("nip_ppnpn") or "PPNPN-2026-001"
        item["unit_kerja"] = item.get("unit_kerja") or "Biro Umum & Keuangan"
        tasks.append(item)

    conn.close()
    return jsonify(tasks)

@app.route("/api/tasks", methods=["POST"])
def create_task():
    role = request.form.get("role", "satpam").strip().lower()
    task_title = request.form.get("task_title", "").strip()
    officer_name = request.form.get("officer_name", "").strip()
    nip_ppnpn = request.form.get("nip_ppnpn", "PPNPN-2026-001").strip()
    unit_kerja = request.form.get("unit_kerja", "Biro Umum & Pengadaan Barang/Jasa").strip()
    shift = request.form.get("shift", "Shift 1 (Pagi)").strip()
    location = request.form.get("location", "").strip()
    status = request.form.get("status", "selesai").strip().lower()
    description = request.form.get("description", "").strip()
    task_time = request.form.get("task_time", "").strip()
    raw_orig_size = request.form.get("original_size", 0)

    if not task_title or not officer_name or not location:
        return jsonify({"error": "Uraian tugas pokok, nama petugas, dan lokasi penugasan wajib diisi."}), 400

    if 'photo' not in request.files or request.files['photo'].filename == '':
        return jsonify({"error": "Foto bukti dukung tugas lapangan wajib dilampirkan."}), 400

    photo_file = request.files['photo']

    try:
        original_size = int(raw_orig_size)
    except (ValueError, TypeError):
        photo_file.seek(0, os.SEEK_END)
        original_size = photo_file.tell()
        photo_file.seek(0)

    if original_size == 0:
        photo_file.seek(0, os.SEEK_END)
        original_size = photo_file.tell()
        photo_file.seek(0)

    # Proses kompresi otomatis
    try:
        saved_filename, compressed_size = compress_and_save_image(photo_file)
    except Exception as e:
        return jsonify({"error": f"Gagal memproses & mengompresi foto: {str(e)}"}), 500

    task_id = uuid.uuid4().hex
    now = datetime.now()
    created_at = now.strftime("%Y-%m-%d %H:%M:%S")

    if not task_time:
        task_time = created_at

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO support_tasks (
            id, role, task_title, officer_name, shift, location,
            status, description, original_size, compressed_size,
            image_filename, task_time, created_at, nip_ppnpn, unit_kerja
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        task_id, role, task_title, officer_name, shift, location,
        status, description, original_size, compressed_size,
        saved_filename, task_time, created_at, nip_ppnpn, unit_kerja
    ))
    conn.commit()
    conn.close()

    return jsonify({
        "message": "Laporan bukti dukung berhasil dicatat & foto otomatis dikompres!",
        "task_id": task_id,
        "compressed_size_fmt": format_size(compressed_size),
        "original_size_fmt": format_size(original_size)
    }), 201

@app.route("/api/tasks/<task_id>/status", methods=["PATCH"])
def update_task_status(task_id):
    data = request.get_json() or {}
    new_status = data.get("status", "").strip().lower()
    if new_status not in ["selesai", "proses", "kendala"]:
        return jsonify({"error": "Status tidak valid. Pilihan: selesai, proses, kendala"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE support_tasks SET status = ? WHERE id = ?", (new_status, task_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()

    if affected == 0:
        return jsonify({"error": "Tugas tidak ditemukan."}), 404

    return jsonify({"message": f"Status tugas diperbarui menjadi '{new_status}'."})

@app.route("/api/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT image_filename FROM support_tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Tugas tidak ditemukan."}), 404

    image_filename = row[0]
    cursor.execute("DELETE FROM support_tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    image_path = UPLOAD_FOLDER / image_filename
    if image_path.exists():
        try:
            image_path.unlink()
        except OSError:
            pass

    return jsonify({"message": "Data tugas dan foto berhasil dihapus."})

@app.route("/api/stats", methods=["GET"])
def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), SUM(original_size), SUM(compressed_size) FROM support_tasks")
    total_count, total_orig, total_comp = cursor.fetchone()
    total_count = total_count or 0
    total_orig = total_orig or 0
    total_comp = total_comp or 0
    total_saved = max(0, total_orig - total_comp)
    percent_saved = (total_saved / total_orig * 100) if total_orig > 0 else 0

    # Hitung per role
    cursor.execute("SELECT role, COUNT(*) FROM support_tasks GROUP BY role")
    role_counts = {r[0]: r[1] for r in cursor.fetchall()}

    # Hitung per status
    cursor.execute("SELECT status, COUNT(*) FROM support_tasks GROUP BY status")
    status_counts = {s[0]: s[1] for s in cursor.fetchall()}

    conn.close()

    return jsonify({
        "total_tasks": total_count,
        "total_original_formatted": format_size(total_orig),
        "total_compressed_formatted": format_size(total_comp),
        "total_saved_formatted": format_size(total_saved),
        "percent_saved": round(percent_saved, 1),
        "by_role": {
            "satpam": role_counts.get("satpam", 0),
            "cleaning": role_counts.get("cleaning", 0),
            "teknisi": role_counts.get("teknisi", 0),
            "driver": role_counts.get("driver", 0),
            "ob": role_counts.get("ob", 0),
            "lainnya": role_counts.get("lainnya", 0)
        },
        "by_status": {
            "selesai": status_counts.get("selesai", 0),
            "proses": status_counts.get("proses", 0),
            "kendala": status_counts.get("kendala", 0)
        }
    })

if __name__ == "__main__":
    print("\n=======================================================")
    print(">> APLIKASI WEB TUGAS PENDUKUNG (SATPAM & STAF OPERASIONAL)")
    print(">> Auto-Kompresi Foto Otomatis Aktif (Client & Server)")
    print(">> Akses di Browser: http://127.0.0.1:5000")
    print("=======================================================\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
