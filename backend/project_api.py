from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter
from pydantic import BaseModel, Field

from core.version import APP_VERSION, PRODUCT_NAME

router = APIRouter(prefix="/api/project", tags=["project"])
PROJECT_ID = "GML-2026-0001"
LLM_TIMEOUT_SECONDS = 12


class AssistantRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)


def _llm_configured() -> bool:
    return bool(os.getenv("OPENAI_API_KEY", "").strip())


def _ask_external_llm(message: str) -> str | None:
    """Call the OpenAI Chat Completions API only when a server-side key exists."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
    payload = json.dumps({
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are the Indonesian-language technical assistant for Game Mod Asset Lab. "
                    "Be accurate, distinguish verified facts from assumptions, never claim tests "
                    "or conversions succeeded unless evidence is provided, and never help bypass "
                    "access controls or process assets without permission."
                ),
            },
            {"role": "user", "content": message},
        ],
        "temperature": 0.2,
    }).encode("utf-8")
    request = Request(
        "https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=LLM_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read(1_000_000).decode("utf-8"))
        reply = data["choices"][0]["message"]["content"]
        return reply.strip() if isinstance(reply, str) and reply.strip() else None
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, KeyError, IndexError):
        # Never expose provider errors or credentials to the client.
        return None


def _built_in_reply(message: str) -> str:
    normalized = message.strip().lower()
    if not normalized:
        return "Tulis pertanyaan terlebih dahulu."
    if any(word in normalized for word in ("error", "bug", "gagal", "eror", "warning")):
        return "Untuk melacak error, jalankan npm run check, python tooling/check.py, lalu python -m pytest -q -W error. Periksa log job CI yang gagal sebelum mengubah kode."
    if any(word in normalized for word in ("screenshot", "tampilan", "preview")):
        return "Jalankan workflow Visual Preview di GitHub Actions. Setelah selesai, unduh artifact screenshot desktop, mobile, dan settings dari halaman run."
    if any(word in normalized for word in ("scraper", "crawl", "ambil halaman")):
        return "Gunakan scraper hanya untuk halaman publik yang boleh diakses. Periksa URL, status HTTP, timeout, robots policy, dan batas halaman. Jangan melewati login, paywall, DRM, atau kontrol akses."
    if any(word in normalized for word in ("build", "test", "ci", "deploy")):
        return "Validasi dengan npm ci, npm run check, python -m pip install -r requirements.txt, python tooling/check.py, dan python -m pytest -q -W error. Pastikan semua job GitHub Actions berstatus Success."
    if any(word in normalized for word in ("asset", "export", "sprite", "lampu", "bussid", "roblox")):
        return "Upload dan inspect asset, periksa metadata dan hasil validasi, lalu uji export pada aplikasi target. ZIP hasil export tidak otomatis berarti format native game sudah dikonversi."
    return "Asisten bawaan memakai aturan sederhana. Untuk jawaban AI generatif, atur OPENAI_API_KEY sebagai secret/environment di server. Jangan pernah menaruh API key di frontend atau repository."


@router.get("/status")
def project_status():
    """Return live project metadata; generated_at is the server's current UTC time."""
    llm_configured = _llm_configured()
    return {
        "project_id": PROJECT_ID,
        "name": PRODUCT_NAME,
        "version": APP_VERSION,
        "status": "operational",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "features": {
            "asset_inspection": True,
            "repository_catalog": True,
            "public_scraper": True,
            "sprite_sheet": True,
            "light_animation": True,
            "assistant": "openai_api" if llm_configured else "built_in_rules",
            "external_llm_configured": llm_configured,
        },
    }


@router.post("/assistant")
def project_assistant(request: AssistantRequest):
    """Use a configured hosted model, with a safe built-in fallback."""
    message = request.message.strip()
    if not message:
        reply = "Tulis pertanyaan terlebih dahulu."
        mode = "built_in_rules"
    else:
        reply = _ask_external_llm(message)
        mode = "openai_api" if reply else "built_in_rules"
        if not reply:
            reply = _built_in_reply(message)
    return {
        "project_id": PROJECT_ID,
        "mode": mode,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "reply": reply,
        "external_llm_configured": _llm_configured(),
    }
