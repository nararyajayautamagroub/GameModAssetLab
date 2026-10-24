# Game Mod Asset Lab v5.0.0

Game Mod Asset Lab adalah aplikasi web untuk inspeksi, klasifikasi, packaging, export, scraper publik, dan pengelolaan asset yang memang dimiliki atau memang boleh diproses oleh pengguna.

## Struktur v5

| Folder | Deskripsi |
|---|---|
| `backend/` | FastAPI application, API routes, gateway, auth, catalog, scraper, dan asset API. |
| `frontend/` | HTML, vanilla JavaScript, CSS responsive, PWA manifest, service worker, dan icon. |
| `core/` | Logic inti yang dipakai bersama backend, tooling, tests, dan adapter platform. |
| `platforms/` | Adapter BUSSID, ETS2/ATS, dan Roblox. |
| `assets/` | Template dan input asset project-level. |
| `artifacts/` | Output runtime seperti generated export dan download artifact. |
| `tooling/` | Scraper CLI, smoke test, frontend smoke, repository audit, dan check pipeline. |
| `tests/` | Test otomatis backend, auth, exporter, image, scraper, dan UI. |
| `docs/` | Dokumentasi arsitektur, deskripsi folder, dan migrasi v5. |

## Fitur aktif

- Asset inspector dengan SHA-256 dan ZIP/TAR inspection.
- Selective export dan manifest JSON.
- Template classifier AO, Texture, dan Kaca/XOR.
- Sprite Sheet inspect dan frame extraction.
- Strobo, Rotator, dan LED Bar animation package.
- Public Roblox Asset Delivery melalui endpoint resmi.
- Register, login, logout, logout-all, profile, settings, dan password change.
- Google Login melalui OpenID Connect jika credential dikonfigurasi.
- 10 bahasa.
- Responsive mobile, tablet, desktop, dan PWA.
- Repository catalog, tree, dan folder description endpoint.
- Public web scraper dengan anti-SSRF dan same-host crawl.

## Website

Frontend utama:

    frontend/index.html
    frontend/app.js
    frontend/styles.css

Backend entrypoint:

    backend/app.py

Footer resmi:

**PT. NARARYA JAYA UTAMA GROUB - All Right Reserved**

## API utama

    GET /api/health
    GET /api/gateway/health
    GET /api/gateway/routes
    GET /api/repository
    GET /api/repository/tree?prefix=...
    GET /api/repository/folders
    GET /api/project/status
    POST /api/project/assistant

Authentication:

    GET /api/auth/status
    POST /api/auth/register
    POST /api/auth/login
    POST /api/auth/logout
    POST /api/auth/logout-all
    PUT /api/auth/settings
    PUT /api/auth/profile
    PUT /api/auth/password

Scraper:

    GET /api/scraper/fetch?url=...
    GET /api/scraper/crawl?url=...&max_pages=...

## Project ID dan asisten bawaan

- Project ID: `GML-2026-0001`.
- `GET /api/project/status` mengembalikan versi, status, fitur, dan timestamp UTC saat request diproses.
- `POST /api/project/assistant` menerima JSON `{"message":"cara memperbaiki error"}` dan memberi panduan berbasis aturan.
- Endpoint asisten mendukung AI generatif melalui OpenAI Chat Completions jika `OPENAI_API_KEY` disetel sebagai environment/secret server. `OPENAI_MODEL` opsional, default `gpt-4o-mini`. Tanpa API key atau jika provider gagal, API kembali ke aturan bawaan. Status provider dibaca dinamis dari konfigurasi server; jawaban real-time bergantung pada koneksi internet, ketersediaan provider, dan kuota API.
- Konfigurasi server: `OPENAI_API_KEY=<secret>` dan opsional `OPENAI_MODEL=gpt-4o-mini`. Jangan menaruh key di frontend, file `.env` yang di-commit, atau log. Provider timeout 12 detik dan error provider tidak dibocorkan ke client.

## Scraper CLI

    python tooling/scraper.py https://example.com
    python tooling/scraper.py https://example.com --crawl --max-pages 5
    python tooling/scraper.py https://example.com --output reports/example.json

Scraper hanya ditujukan untuk resource publik dan tidak melewati login, paywall, private resource, DRM, atau access control.

## Instalasi

    npm install
    npm run check
    npm start

Python validation:

    python -m pip install -r requirements.txt
    python tooling/check.py

Local server:

    http://127.0.0.1:8000

## Google Login

    GOOGLE_CLIENT_ID=...
    GOOGLE_CLIENT_SECRET=...
    GOOGLE_REDIRECT_URI=https://domain.example/api/auth/google/callback

Untuk HTTPS:

    COOKIE_SECURE=1
    SESSION_SECRET=<random-secret-panjang>

Jangan menyimpan secret di repository.

## Validation

    npm run frontend:smoke
    python tooling/repository_audit.py
    python tooling/smoke.py
    python -m pytest -q -W error

CI menjalankan npm check, pip check, compileall, Ruff, pytest, dan runtime smoke.

## Batas keamanan

Project tidak membypass password, enkripsi, DRM, signature, private asset, atau access control.

Untuk format proprietary, tool hanya mengklaim kemampuan yang benar-benar tersedia. Export ZIP tidak berarti format native game telah dikonversi.

## Version

Game Mod Asset Lab v5.0.0
