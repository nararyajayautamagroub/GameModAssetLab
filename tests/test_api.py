import asyncio

import httpx

from backend.app import app


def request(path: str) -> httpx.Response:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.get(path)

    return asyncio.run(run())


def test_health():
    response = request("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "5.0.0"


def test_template_types():
    response = request("/api/templates/types")
    assert response.status_code == 200
    assert response.json()["xor"] == "Kaca/XOR"


def test_capabilities():
    response = request("/api/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["repository_sync"] is True
    assert data["languages"] == 10
    assert "profile" in data["settings"]


def test_repository_catalog_contains_platforms():
    response = request("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert "bussid" in data
    assert "ets2_ats" in data
    assert "roblox" in data


def test_path_security_blocks_outside_files():
    response = request("/api/templates/classify?path=/etc/passwd")
    assert response.status_code == 400


def test_scraper_route_rejects_local_target():
    response = request("/api/scraper/fetch?url=http%3A%2F%2F127.0.0.1%3A8000%2F")
    assert response.status_code == 400


def test_security_headers_and_pwa():
    response = request("/api/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    manifest = request("/manifest.webmanifest")
    assert manifest.status_code == 200
    assert manifest.headers["content-type"].startswith("application/manifest+json")

    worker = request("/sw.js")
    assert worker.status_code == 200
    assert worker.headers["content-type"].startswith("application/javascript")


def test_crawl_route_rejects_invalid_limits():
    response = request(
        "/api/scraper/crawl?url=https%3A%2F%2Fexample.com%2F&max_bytes=0"
    )
    assert response.status_code == 400


def test_frontend_assets_and_gateway():
    css = request("/styles.css")
    assert css.status_code == 200
    assert css.headers["content-type"].startswith("text/css")

    js = request("/app.js")
    assert js.status_code == 200
    assert "function api" in js.text

    gateway = request("/api/gateway/health")
    assert gateway.status_code == 200
    assert gateway.json()["gateway"] == "fastapi"
    assert gateway.json()["version"] == "5.0.0"

def test_repository_folder_descriptions():
    response = request("/api/repository/folders")
    assert response.status_code == 200
    folders = response.json()["folders"]
    assert folders["backend"]
    assert folders["frontend"]
    assert folders["core"]
    assert folders["platforms"]


def test_repository_catalog_uses_current_repository_name():
    from backend.catalog import repository_folders

    data = repository_folders()
    assert data["repository"] == "nararyajayautamagroub/GameModAssetLab"
    assert data["version"] == "5.0.0"


def post_json(path: str, payload: dict) -> httpx.Response:
    async def run() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.post(path, json=payload)

    return asyncio.run(run())


def test_project_status_reports_server_timestamp_and_ai_mode(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = request("/api/project/status")
    assert response.status_code == 200
    data = response.json()
    assert data["project_id"] == "GML-2026-0001"
    assert data["features"]["external_llm_configured"] is False
    assert data["features"]["assistant"] == "built_in_rules"
    assert data["generated_at"].endswith("+00:00")


def test_assistant_uses_rules_without_provider_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = post_json(
        "/api/project/assistant", {"message": "cara memperbaiki error"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "built_in_rules"
    assert "pytest" in data["reply"]
    assert data["external_llm_configured"] is False


def test_assistant_uses_configured_ai_provider(monkeypatch):
    from backend import project_api

    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-a-real-secret")
    monkeypatch.setattr(
        project_api, "_ask_external_llm", lambda message: "Jawaban AI simulasi."
    )
    response = post_json(
        "/api/project/assistant", {"message": "Jelaskan project ini"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "openai_api"
    assert data["reply"] == "Jawaban AI simulasi."
    assert data["external_llm_configured"] is True
