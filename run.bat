@echo off
title SiTugas - Web Manajemen Tugas Pendukung & Auto Kompres Foto
cd /d "%~dp0"

echo =======================================================
echo   SISTEM MANAJEMEN TUGAS PENDUKUNG (SiTugas)
echo   (Satpam, Cleaning Service, Teknisi, Driver, OB)
echo   Dengan Auto-Kompresi Foto Otomatis (Dual Layer)
echo =======================================================
echo.
echo Sedang menyiapkan server lokal...
echo Membuka browser ke http://127.0.0.1:5000 dalam 2 detik...
echo.

start "" http://127.0.0.1:5000
python app.py

pause
