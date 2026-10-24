from pathlib import Path
from tempfile import TemporaryDirectory
import os
import secrets

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from core.auth_db import init_db
from core.light_animation import VALID_LIGHT_TYPES, build_animation, to_dict
from core.package_export import export_light_package
from core.version import APP_VERSION, PRODUCT_NAME
from backend.asset_api import router as asset_router
from backend.auth_api import GOOGLE_CONFIGURED, router as auth_router
from backend.catalog import repository_catalog, repository_folders, repository_tree
from backend.gateway_api import router as gateway_router
from backend.i18n_api import router as i18n_router
from backend.scraper_api import router as scraper_router
from backend.sprite_api import router as sprite_router
from backend.template_api import router as template_router
from backend.project_api import router as project_router

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
GENERATED = ROOT / "artifacts" / "generated"
GENERATED.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=PRODUCT_NAME, version=APP_VERSION)
init_db()
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET") or secrets.token_hex(32),
    session_cookie="oauth_session",
    max_age=900,
    same_site="lax",
    https_only=os.getenv("COOKIE_SECURE", "0") == "1",
)
app.include_router(asset_router)
app.include_router(template_router)
app.include_router(sprite_router)
app.include_router(scraper_router)
app.include_router(auth_router)
app.include_router(i18n_router)
app.include_router(gateway_router)
app.include_router(project_router)


@app.get("/", tags=["web"])
def index():
    return FileResponse(FRONTEND / "index.html")


@app.get("/manifest.webmanifest", tags=["pwa"])
def manifest():
    return FileResponse(FRONTEND / "manifest.webmanifest", media_type="application/manifest+json")


@app.get("/sw.js", tags=["pwa"])
def service_worker():
    return FileResponse(FRONTEND / "sw.js", media_type="application/javascript")


@app.get("/icon.svg", tags=["pwa"])
def icon():
    return FileResponse(FRONTEND / "icon.svg", media_type="image/svg+xml")


@app.get("/api/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "service": "game-mod-asset-lab",
        "version": app.version,
        "google_login": GOOGLE_CONFIGURED,
    }


@app.get("/api/categories", tags=["catalog"])
def categories():
    return repository_catalog()["categories"]


@app.get("/api/repository/tree", tags=["catalog"])
def repository_tree_endpoint(prefix: str = ""):
    return repository_tree(prefix)


@app.get("/api/repository/folders", tags=["catalog"])
def repository_folders_endpoint():
    return repository_folders()


@app.get("/api/repository", tags=["catalog"])
def repository():
    return repository_catalog()


@app.get("/api/capabilities", tags=["system"])
def capabilities():
    return {
        "inspect_archive": True,
        "selective_export": True,
        "template_classification": ["ao", "texture", "xor"],
        "light_animation_package": ["strobo", "rotator", "ledbar"],
        "roblox_public_asset_download": True,
        "roblox_studio_light_script_export": True,
        "native_rbxm_generation": False,
        "native_proprietary_game_format_decode": False,
        "encryption_drm_bypass": False,
        "repository_sync": True,
        "authentication": ["local_register", "local_login", "session_logout", "google_oauth"],
        "settings": ["profile", "language", "theme", "notifications", "password_change"],
        "languages": 10,
        "pwa": True,
        "scraper": True,
        "scraper_crawl": True,
        "repository_folder_descriptions": True,
        "version": APP_VERSION,
    }


@app.get("/api/lights/{light_type}", tags=["lights"])
def preview(light_type: str, fps: int = 30):
    if light_type not in VALID_LIGHT_TYPES:
        raise HTTPException(status_code=404, detail="Jenis lampu tidak dikenal.")
    try:
        return to_dict(build_animation(light_type, fps))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/lights/{light_type}/download", tags=["lights"])
def download(light_type: str, platform: str = "roblox"):
    if light_type not in VALID_LIGHT_TYPES:
        raise HTTPException(status_code=404, detail="Jenis lampu tidak dikenal.")
    if platform not in {"roblox", "bussid"}:
        raise HTTPException(status_code=400, detail="Platform tidak didukung.")

    with TemporaryDirectory() as tmp:
        path = export_light_package(light_type, Path(tmp) / f"{platform}_{light_type}", platform)
        data = path.read_bytes()

    output = GENERATED / path.name
    output.write_bytes(data)
    return FileResponse(output, filename=output.name, media_type="application/zip")


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if request.url.path.startswith("/api/auth"):
        response.headers["Cache-Control"] = "no-store"
    return response


app.mount("/", StaticFiles(directory=FRONTEND, html=False), name="frontend-static")
