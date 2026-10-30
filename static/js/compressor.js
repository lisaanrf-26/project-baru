/**
 * Client-Side Auto Photo Compressor for SiTugas
 * Mengompres foto kamera/file seketika di browser sebelum dikirim ke server.
 */

window.SiTugasCompressor = {
    originalFile: null,
    compressedBlob: null,
    compressedDataUrl: null,
    originalSize: 0,
    compressedSize: 0,
    
    formatBytes: function(bytes, decimals = 1) {
        if (!bytes || bytes === 0) return '0 B';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },

    /**
     * Kompres file gambar secara instan
     * @param {File} file 
     * @param {Object} options 
     * @returns {Promise<{blob: Blob, dataUrl: string, originalSize: number, compressedSize: number, savedPercent: number}>}
     */
    compressImage: function(file, options = {}) {
        const startTime = performance.now();
        const maxDim = options.maxDim || 1400;
        const quality = options.quality || 0.78;
        const addWatermark = options.watermark !== false;
        const officerName = options.officerName || 'Petugas Lapangan';
        const roleName = options.roleName || 'Tugas Pendukung';

        this.originalFile = file;
        this.originalSize = file.size;

        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onerror = () => reject(new Error("Gagal membaca file gambar"));
            reader.onload = (e) => {
                const img = new Image();
                img.onerror = () => reject(new Error("Format gambar tidak didukung"));
                img.onload = () => {
                    let { width, height } = img;

                    // Hitung dimensi baru proporsional
                    if (width > maxDim || height > maxDim) {
                        if (width > height) {
                            height = Math.round((height * maxDim) / width);
                            width = maxDim;
                        } else {
                            width = Math.round((width * maxDim) / height);
                            height = maxDim;
                        }
                    }

                    const canvas = document.createElement('canvas');
                    canvas.width = width;
                    canvas.height = height;
                    const ctx = canvas.getContext('2d');

                    // Gambar gambar utama
                    ctx.drawImage(img, 0, 0, width, height);

                    // Tambahkan Watermark Resmi Stempel Waktu (Jika diaktifkan)
                    if (addWatermark) {
                        SiTugasCompressor.drawWatermark(ctx, width, height, officerName, roleName, options);
                    }

                    // Tentukan format kompresi (prioritaskan image/webp, fallback ke image/jpeg)
                    let mimeType = 'image/webp';
                    
                    canvas.toBlob((blob) => {
                        if (!blob) {
                            // Fallback jika webp tidak didukung
                            mimeType = 'image/jpeg';
                            canvas.toBlob((fallbackBlob) => {
                                finalize(fallbackBlob);
                            }, 'image/jpeg', quality);
                        } else {
                            finalize(blob);
                        }
                    }, mimeType, quality);

                    function finalize(finalBlob) {
                        const endTime = performance.now();
                        const durationMs = Math.round(endTime - startTime);
                        SiTugasCompressor.compressedBlob = finalBlob;
                        SiTugasCompressor.compressedSize = finalBlob.size;
                        
                        const savedBytes = Math.max(0, file.size - finalBlob.size);
                        const savedPercent = file.size > 0 ? ((savedBytes / file.size) * 100).toFixed(1) : 0;
                        const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
                        SiTugasCompressor.compressedDataUrl = dataUrl;

                        resolve({
                            blob: finalBlob,
                            dataUrl: dataUrl,
                            originalSize: file.size,
                            compressedSize: finalBlob.size,
                            savedBytes: savedBytes,
                            savedPercent: savedPercent,
                            durationMs: durationMs,
                            dimensions: { width, height }
                        });
                    }
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        });
    },

    /**
     * Stempel Watermark Resmi Bukti Lapangan
     */
    drawWatermark: function(ctx, width, height, officerName, roleName, options = {}) {
        const now = new Date();
        const days = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"];
        const dayStr = days[now.getDay()];
        const dateStr = now.toLocaleDateString('id-ID', { day: '2-digit', month: 'short', year: 'numeric' });
        const timeStr = now.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' WIB';

        const loc = options.location || 'Area Lokasi Penugasan';

        const titleHeader = `DOKUMENTASI BUKTI TUGAS LAPANGAN`;
        const line1 = `${roleName.toUpperCase()}`;
        const line2 = `Petugas: ${officerName}`;
        const line3 = `Lokasi: ${loc}`;
        const line4 = `${dayStr}, ${dateStr} • ${timeStr} (VERIFIED)`;

        const baseFontSize = Math.max(12, Math.round(width * 0.020));
        ctx.font = `700 ${baseFontSize}px 'Plus Jakarta Sans', system-ui, sans-serif`;

        const maxTextWidth = Math.max(
            ctx.measureText(titleHeader).width,
            ctx.measureText(line1).width,
            ctx.measureText(line2).width,
            ctx.measureText(line3).width,
            ctx.measureText(line4).width
        );

        const paddingX = 16;
        const paddingY = 12;
        const boxWidth = maxTextWidth + (paddingX * 2);
        const boxHeight = (baseFontSize * 5.2) + (paddingY * 2);

        const posX = width - boxWidth - 16;
        const posY = height - boxHeight - 16;

        ctx.save();

        // Background box gelap elegan modern
        ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
        ctx.beginPath();
        if (ctx.roundRect) {
            ctx.roundRect(posX, posY, boxWidth, boxHeight, 10);
        } else {
            ctx.rect(posX, posY, boxWidth, boxHeight);
        }
        ctx.fill();

        // Border tipis elegan
        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Header Title
        ctx.fillStyle = '#60a5fa';
        ctx.font = `800 ${Math.round(baseFontSize * 0.95)}px 'Plus Jakarta Sans', system-ui, sans-serif`;
        ctx.textBaseline = 'top';
        ctx.fillText(titleHeader, posX + paddingX, posY + paddingY);

        // Line 1: Kategori Divisi
        ctx.fillStyle = '#ffffff';
        ctx.font = `700 ${Math.round(baseFontSize * 1.05)}px 'Plus Jakarta Sans', system-ui, sans-serif`;
        ctx.fillText(line1, posX + paddingX, posY + paddingY + baseFontSize * 1.3);

        // Line 2: Nama Petugas
        ctx.fillStyle = '#e2e8f0';
        ctx.font = `500 ${Math.round(baseFontSize * 0.9)}px 'Plus Jakarta Sans', system-ui, sans-serif`;
        ctx.fillText(line2, posX + paddingX, posY + paddingY + baseFontSize * 2.5);

        // Line 3: Lokasi
        ctx.fillStyle = '#cbd5e1';
        ctx.font = `400 ${Math.round(baseFontSize * 0.85)}px 'Plus Jakarta Sans', system-ui, sans-serif`;
        ctx.fillText(line3, posX + paddingX, posY + paddingY + baseFontSize * 3.6);

        // Line 4: Waktu Realtime
        ctx.fillStyle = '#34d399'; // Emerald green
        ctx.font = `600 ${Math.round(baseFontSize * 0.85)}px 'Plus Jakarta Sans', system-ui, sans-serif`;
        ctx.fillText(line4, posX + paddingX, posY + paddingY + baseFontSize * 4.7);

        ctx.restore();
    }
};
