# 🔒 Security Policy — Tani Cerdas AI Assistant

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.x (Agentic)  | ✅ Aktif didukung |
| 1.x (Legacy)   | ⚠️ Hanya security patch |

---

## Credential Rotation Notice

> **Tanggal**: 13–14 Agustus 2026

Selama proses audit keamanan komprehensif, beberapa credential yang sebelumnya ter-commit ke repositori dalam commit awal (`38dd252`, sebelum 13 Agustus 2026) telah diidentifikasi dan **segera dirotasi**:

| Credential | Tindakan |
|---|---|
| `OPENWEATHER_API_KEY` (key lama di `Weather.jsx`) | ✅ **Dirotasi** — key lama dinonaktifkan di dashboard OpenWeatherMap |
| `x-api-key` header di `netlify.toml` | ✅ **Dihapus** — file konfigurasi diperbaiki, key tidak lagi digunakan |
| `ENCRYPTION_KEY` (Fernet key lama) | ✅ **Dirotasi** — key baru di-generate (`KrHpz0_...`) dan hanya disimpan di `.env` lokal yang tidak di-track Git |

**Catatan teknis**: Meskipun nilai lama ada dalam commit sebelum 13 Agustus 2026, semua API yang terpengaruh telah dinonaktifkan/dirotasi dari sisi provider sehingga nilai historis tersebut tidak lagi dapat digunakan untuk akses tidak sah.

---

## Reporting a Vulnerability

Jika Anda menemukan kerentanan keamanan di proyek ini:

1. **Jangan** membuka GitHub Issue publik untuk kerentanan keamanan.
2. Kirim laporan detail ke: `tbimantara04@gmail.com`
3. Sertakan:
   - Deskripsi kerentanan
   - Langkah reproduksi
   - Dampak yang memungkinkan
4. Anda akan mendapat respons dalam **72 jam**.

---

## Security Architecture

### Credential Management
- Semua secret disimpan di file `.env` yang **tidak pernah di-commit** (dikecualikan via `.gitignore` aturan `*.env`)
- Template credential tersedia di `.env.example` dan `backend/.env.example`
- Enkripsi data sensitif (histori chat, profil petani) menggunakan **AES-256 via Fernet**

### API Security
- CORS dibatasi ke `ALLOWED_ORIGINS` dari environment variable
- Guardrails aktif untuk mencegah prompt injection dan query di luar domain pertanian
- Workflow Security — daftar putih tindakan yang diizinkan per agen (mencegah eksekusi metode berbahaya)

### Data Integrity
- FAISS vector index dilindungi checksum SHA-256 sebelum deserialisasi

---

## Security Audit History

| Tanggal | Auditor | Temuan | Status |
|---|---|---|---|
| 13 Agt 2026 | Internal | Hardcoded secret × 2, CORS wildcard, FAISS unsafe deserialization | ✅ Diperbaiki |
| 14 Agt 2026 | Internal | 5 bare except, missing integration tests, unpinned deps | ✅ Diperbaiki |
| 15 Agt 2026 | Eksternal (Dosen) | Saran rotasi key historis | ✅ Didokumentasikan & Dikonfirmasi |
