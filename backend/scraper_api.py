from __future__ import annotations

from fastapi import APIRouter, HTTPException

from core.scraper import crawl_site, scrape_page

router = APIRouter(prefix="/api/scraper", tags=["scraper"])


@router.get("/fetch")
def fetch(
    url: str,
    max_bytes: int = 5 * 1024 * 1024,
    max_links: int = 100,
    timeout: int = 10,
):
    try:
        return scrape_page(
            url,
            max_bytes=max_bytes,
            max_links=max_links,
            timeout=timeout,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/crawl")
def crawl(
    url: str,
    max_pages: int = 10,
    max_links_per_page: int = 50,
    max_bytes: int = 5 * 1024 * 1024,
    timeout: int = 10,
):
    try:
        return crawl_site(
            url,
            max_pages=max_pages,
            max_links_per_page=max_links_per_page,
            max_bytes=max_bytes,
            timeout=timeout,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/strategies")
def scraper_strategies():
    """Expose the ten extraction checks used to guide public-page scraping.

    These are extraction strategies, not ten independent external APIs. They all
    operate on a URL the caller is authorized to access through the existing
    SSRF-protected fetch/crawl pipeline.
    """
    strategies = [
        {"id": "document_metadata", "name": "Document metadata", "purpose": "Title, description, canonical URL, and language"},
        {"id": "headings", "name": "Heading outline", "purpose": "H1-H6 structure for page summarization"},
        {"id": "links", "name": "Link discovery", "purpose": "Public same-host links for bounded crawl"},
        {"id": "images", "name": "Image references", "purpose": "Image URLs and alt text"},
        {"id": "structured_data", "name": "Structured data", "purpose": "JSON-LD and schema.org data when present"},
        {"id": "open_graph", "name": "Open Graph", "purpose": "Social preview metadata"},
        {"id": "microdata", "name": "Microdata", "purpose": "Itemprop/itemtype hints when present"},
        {"id": "tables", "name": "Table extraction", "purpose": "Tabular public-page content"},
        {"id": "feeds", "name": "Feed discovery", "purpose": "Linked RSS/Atom feed declarations"},
        {"id": "content_signals", "name": "Content signals", "purpose": "Robots directives, charset, and content type"},
    ]
    return {
        "pipeline": "public-page-extraction",
        "strategy_count": len(strategies),
        "independent_api_count": 0,
        "strategies": strategies,
        "limits": {
            "authentication_bypass": False,
            "same_host_crawl": True,
            "ssrf_protection": True,
            "data_accuracy": "Depends on source content and availability; no scraper can guarantee 100% accuracy.",
        },
    }
