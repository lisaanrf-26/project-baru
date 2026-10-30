# 🛡️ SiTugas - Sistem Manajemen Tugas Pendukung & Auto-Kompres Foto

Aplikasi web modern dengan antarmuka **Menu Ikon Bersih & Responsif**, dirancang khusus untuk pencatatan dan pelaporan dokumentasi kegiatan **Petugas Pendukung Lapangan** (Satpam / Security, Cleaning Service, Teknisi & Maintenance, Driver / Pengemudi, dan Office Boy / OB).

Dilengkapi teknologi **Auto-Kompresi Foto Otomatis (Dual Layer)**: saat petugas mengambil foto dari kamera HP atau memilih berkas foto resolusi tinggi (5 MB – 12 MB), sistem **langsung otomatis mengompres foto dalam hitungan milidetik** menjadi ukuran ringan (~150 KB – 250 KB WebP) tanpa mengurangi kejelasan bukti visual tugas!

---

## ✨ Fitur-Fitur Utama

1. **Menu Beranda Berbasis Ikon (Klik Ikon Masuk ke Halaman)**:
   - 🛡️ **Satpam (Security)**: Patroli titik pantau, pos gerbang utama, serah terima jaga, cek gembok & pintu malam.
   - 🧹 **Cleaning Service**: Pembersihan toilet, sapu/pel lobi & selasar, penanganan tempat sampah, pembersihan kaca.
   - 🔧 **Teknisi & Maintenance**: Pengecekan suhu & filter AC, panel listrik, uji coba genset rutin, pompa air & tandon.
   - 🚗 **Driver / Pengemudi**: Pengecekan armada kendaraan, logbook KM & BBM, antar-jemput dinas, cuci mobil.
   - ☕ **Office Boy (OB)**: Persiapan ruang rapat & audio, stok air galon pantry, penataan fasilitas & distribusi surat.
   - 📋 **Semua Logbook Tugas**: Tabel rekapitulasi terpadu seluruh kegiatan tugas dari semua divisi.
   - 🖨️ **Cetak Laporan**: Siap cetak ke kertas atau simpan ke PDF.
   - ⚡ **Efisiensi Kompresi**: Statistik penghematan kuota data & memori server.

2. **Auto-Kompresi Foto Otomatis Seketika (Instant Auto-Compress)**:
   - Begitu foto dipilih/dijepret via kamera HP, engine HTML5 Canvas langsung mengompres resolusi tinggi menjadi ringan dalam < 150 milidetik.
   - Kartu perbandingan real-time: menampilkan ukuran asli (dicoret) ➔ ukuran terkompres ➔ persentase penghematan (misal: `-96.2%`).
   - Upload super cepat (0.2 detik) dan hemat kuota internet lapangan.
   - Dilengkapi stempel tanggal & jam WIB otomatis di foto sebagai bukti otentik kegiatan.

3. **Navigasi Cepat & Nyaman**:
   - Klik ikon divisi ➔ langsung masuk ke halaman kerja khusus divisi tersebut.
   - Tombol **`← Menu Ikon`** di bagian atas untuk kembali ke beranda kapan saja.
   - Template cepat 1-klik untuk mengisi form tugas tanpa perlu mengetik panjang di HP.

### 2. Auto-Kompresi Foto Otomatis Seketika (Instant Auto-Compress)
- **Kompresi Langsung di Sisi Klien (Browser/HP)**: Begitu foto dipilih/dijepret via kamera, foto resolusi tinggi langsung diolah melalui HTML5 Canvas engine.
- **Kartu Hasil Kompresi Real-Time**: Langsung menampilkan perbandingan:
  - *Ukuran Awal*: contoh `6.2 MB` (dicoret)
  - *Ukuran Terkompresi*: contoh `215 KB`
  - *Persentase Penghematan*: `-96.5%`
- **Upload Super Cepat**: Data yang dikirim ke server berukuran kecil sehingga proses upload hanya memakan waktu 0.2 detik, sangat ramah kuota dan lancar di jaringan HP yang lemah.
- **Stempel Watermark Resmi**: Dilengkapi opsi stempel waktu otomatis (Hari, Tanggal, Jam WIB, Nama Petugas, Divisi) di sudut foto sebagai bukti otentik kegiatan tugas lapangan.
- **Optimasi Server-Side**: Server Flask & Pillow mengoptimasi format WebP dan otomatis memperbaiki orientasi foto yang miring dari kamera smartphone (EXIF rotation auto-correction).

### 3. Manajemen Shift & Status Tugas
- Pilihan Shift: **Shift 1 (Pagi)**, **Shift 2 (Siang)**, **Shift 3 (Malam)**, dan **Non-Shift / Reguler**.
- Pilihan Status: **🟢 Selesai**, **🟡 Sedang Dikerjakan**, dan **🔴 Butuh Tindak Lanjut / Kendala**.
- Pengubahan status tugas secara instan dengan 1 kali klik pada daftar tugas.

### 4. Feed Visual, Filter & Pencarian
- Mode Tampilan Ganda: **Kartu Visual (Feed)** untuk melihat foto besar & detail, atau **Tabel Ringkas (Logbook)**.
- Filter satu klik berdasarkan Divisi (Satpam, Cleaning, Teknisi, Driver, OB).
- Filter berdasarkan Status dan pencarian teks cepat (nama petugas, lokasi, judul tugas).

### 5. Cetak / Ekspor Logbook Harian Resmi
- Terdapat tombol **Cetak Logbook** dengan tata letak printer-friendly siap cetak ke kertas atau simpan ke PDF lengkap dengan kolom tanda tangan Petugas Pelaksana, Danru / Koordinator Lapangan, dan Building Manager / Pengawas.

---

## 🚀 Cara Menjalankan

### Cara 1: Menggunakan Shortcut Batch (Paling Praktis)
Cukup klik ganda (double-click) berkas:
👉 **`run.bat`**

Browser akan otomatis terbuka mengarah ke **`http://127.0.0.1:5000`**.

---

### Cara 2: Melalui Terminal / PowerShell
1. Buka PowerShell atau Command Prompt.
2. Masuk ke direktori projek:
   ```powershell
   cd "C:\Users\ADVAN\.gemini\antigravity\scratch\tugas-pendukung"
   ```
3. Jalankan server Flask:
   ```powershell
   python app.py
   ```
4. Buka di browser favorit Anda:
   👉 **`http://127.0.0.1:5000`**

---

## 📁 Struktur Berkas

```
tugas-pendukung/
├── app.py                 # Backend Flask, REST API, SQLite database & image processing
├── requirements.txt       # Daftar dependensi (Flask, Pillow)
├── run.bat                # Launcher 1-klik untuk Windows
├── seed_sample_data.py    # Script pengisi data contoh awal (Satpam, CS, Teknisi)
├── test_app.py            # Unit test verifikasi endpoint & kompresi foto
├── README.md              # Dokumentasi lengkap
├── static/
│   └── js/
│       └── compressor.js  # Engine auto-kompresi foto instan & stempel watermark
├── templates/
│   └── index.html         # Antarmuka web responsif (Tailwind CSS, UI modern, Cetak Logbook)
├── uploads/               # Penyimpanan foto tugas terkompresi (format WebP)
└── tasks.db               # Database SQLite lokal
```
