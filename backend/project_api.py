from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel, Field

from core.version import APP_VERSION, PRODUCT_NAME

router = APIRouter(prefix="/api/project", tags=["project"])
PROJECT_ID = "GML-2026-0001"

class AssistantRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)

@router.get("/status")
def project_status():
    """Return live project metadata; generated_at is the server's current UTC time."""
    return {
        "project_id": PROJECT_ID,
        "name": PRODUCT_NAME,
        "version": APP_VERSION,
        "status": "operational",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "features": {"asset_inspection": True, "repository_catalog": True, "public_scraper": True, "sprite_sheet": True, "light_animation": True, "assistant": "built_in_rules", "external_llm_configured": False},
    }

@router.post("/assistant")
def project_assistant(request: AssistantRequest):
    """Transparent built-in helper, not a hosted LLM."""
    message = request.message.strip().lower()
    if not message:
        reply = "Tulis pertanyaan terlebih dahulu."
    elif any(word in message for word in ("error", "bug", "gagal", "eror", "warning")):
        reply = "Untuk melacak error, jalankan npm run check, python tooling/check.py, lalu python -m pytest -q -W error. Periksa log job CI yang gagal sebelum mengubah kode."
    elif any(word in message for word in ("screenshot", "tampilan", "preview")):
        reply = "Jalankan workflow Visual Preview di GitHub Actions. Setelah selesai, unduh artifact screenshot desktop, mobile, dan settings dari halaman run."
    elif any(word in message for word in ("scraper", "crawl", "ambil halaman")):
        reply = "Gunakan scraper hanya untuk halaman publik yang boleh diakses. Periksa URL, status HTTP, timeout, robots policy, dan batas halaman. Jangan melewati login, paywall, DRM, atau kontrol akses."
    elif any(word in message for word in ("build", "test", "ci", "deploy")):
        reply = "Validasi dengan npm ci, npm run check, python -m pip install -r requirements.txt, python tooling/check.py, dan python -m pytest -q -W error. Pastikan semua job GitHub Actions berstatus Success."
    elif any(word in message for word in ("asset", "export", "sprite", "lampu", "bussid", "roblox")):
        reply = "Upload dan inspect asset, periksa metadata dan hasil validasi, lalu uji export pada aplikasi target. ZIP hasil export tidak otomatis berarti format native game sudah dikonversi."
    else:
        reply = "Asisten bawaan ini menggunakan aturan sederhana, bukan model AI generatif. Untuk AI eksternal, integrasikan penyedia model melalui backend dan simpan API key di environment server, bukan di frontend atau repository."
    return {"project_id": PROJECT_ID, "mode": "built_in_rules", "generated_at": datetime.now(timezone.utc).isoformat(), "reply": reply, "external_llm_configured": False}
