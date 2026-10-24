from __future__ import annotations

import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
GITHUB_REPO = os.getenv(
    "GITHUB_REPO", "nararyajayautamagroub/GameModAssetLab"
)
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}"
_REMOTE_CACHE: tuple[float, dict] | None = None
CACHE_SECONDS = 15
FOLDER_DESCRIPTIONS = {
    "backend": "FastAPI API, authentication, scraper, catalog, gateway, and asset endpoints.",
    "frontend": "Responsive HTML, vanilla JavaScript, CSS, and PWA files.",
    "core": "Reusable Python domain services shared by backend, tooling, and platform adapters.",
    "platforms": "Platform-specific adapters for BUSSID, ETS2/ATS, and Roblox.",
    "assets": "Project asset templates and static inputs.",
    "artifacts": "Generated exports, downloads, and runtime output.",
    "tooling": "Validation, scraper CLI, smoke tests, and repository audit tools.",
    "tests": "Automated test suite for backend, core services, scraper, exports, and UI.",
    "docs": "Architecture, migration, folder descriptions, and operating documentation.",
}
IGNORED_LOCAL_PARTS = {"__pycache__", ".git", "uploads", "artifacts", "data"}


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORED_LOCAL_PARTS for part in path.parts)


def _local_catalog() -> dict:
    categories = {}
    for platform in ("bussid", "ets2_ats", "roblox"):
        platform_root = ROOT / "platforms" / platform
        if not platform_root.is_dir():
            continue
        categories[platform] = {}
        for folder in sorted(p for p in platform_root.iterdir() if p.is_dir()):
            files = [
                p.relative_to(folder).as_posix()
                for p in sorted(folder.rglob("*"))
                if p.is_file() and not _is_ignored(p)
            ]
            categories[platform][folder.name] = {
                "files": files,
                "count": len(files),
            }

    template_root = ROOT / "assets" / "templates"
    templates = (
        [
            p.relative_to(ROOT).as_posix()
            for p in sorted(template_root.rglob("*"))
            if p.is_file() and not _is_ignored(p)
        ]
        if template_root.is_dir()
        else []
    )

    return {
        "source": "local_repository",
        "repository": GITHUB_REPO,
        "categories": categories,
        "templates": templates,
        "folder_descriptions": FOLDER_DESCRIPTIONS,
    }


def _json_request(url: str) -> dict:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Game-Mod-Asset-Lab/5.0",
        },
    )
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def _github_catalog() -> dict:
    global _REMOTE_CACHE
    now = time.time()
    if _REMOTE_CACHE and now - _REMOTE_CACHE[0] < CACHE_SECONDS:
        return _REMOTE_CACHE[1]

    repository = _json_request(GITHUB_API)
    default_branch = repository.get("default_branch", "main")
    commit = _json_request(f"{GITHUB_API}/commits/{default_branch}")
    tree = _json_request(
        f"{GITHUB_API}/git/trees/{commit['sha']}?recursive=1"
    )

    files = [
        item["path"]
        for item in tree.get("tree", [])
        if item.get("type") == "blob"
    ]
    data = {
        "source": "github",
        "repository": GITHUB_REPO,
        "default_branch": default_branch,
        "commit_sha": commit.get("sha"),
        "commit_message": commit.get("commit", {}).get("message", "").splitlines()[0],
        "commit_date": commit.get("commit", {}).get("committer", {}).get("date"),
        "tree_sha": tree.get("sha"),
        "file_count": len(files),
        "files": files,
        "truncated": bool(tree.get("truncated", False)),
        "updated_at": time.time(),
    }
    _REMOTE_CACHE = (now, data)
    return data


def repository_catalog() -> dict:
    local = _local_catalog()
    try:
        local["remote"] = _github_catalog()
        local["remote_status"] = "ok"
    except (HTTPError, URLError, TimeoutError, ValueError, OSError, KeyError) as exc:
        local["remote"] = None
        local["remote_status"] = f"unavailable: {exc}"
    return local


def repository_tree(prefix: str = "") -> dict:
    prefix = prefix.strip().strip("/")
    try:
        remote = _github_catalog()
        files = remote["files"]
        source = "github"
        payload = {
            "repository": remote["repository"],
            "default_branch": remote["default_branch"],
            "commit_sha": remote["commit_sha"],
            "tree_sha": remote["tree_sha"],
            "truncated": remote["truncated"],
            "updated_at": remote["updated_at"],
        }
    except (HTTPError, URLError, TimeoutError, ValueError, OSError, KeyError) as exc:
        local = _local_catalog()
        files = [
            str(path.relative_to(ROOT))
            for path in sorted(ROOT.rglob("*"))
            if path.is_file() and not _is_ignored(path)
        ]
        source = "local_repository"
        payload = {
            "repository": local["repository"],
            "default_branch": None,
            "commit_sha": None,
            "tree_sha": None,
            "truncated": False,
            "updated_at": time.time(),
            "remote_status": f"unavailable: {exc}",
        }

    if prefix:
        files = [
            item
            for item in files
            if item == prefix or item.startswith(prefix + "/")
        ]

    return {
        "source": source,
        **payload,
        "prefix": prefix,
        "file_count": len(files),
        "files": files,
    }


def repository_folders() -> dict:
    return {
        "repository": GITHUB_REPO,
        "version": "5.0.0",
        "folders": FOLDER_DESCRIPTIONS,
    }
