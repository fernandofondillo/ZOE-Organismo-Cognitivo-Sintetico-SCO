"""Handlers de marketplace: /api/marketplace/* (5 endpoints)."""

from pathlib import Path
from typing import Any

from aiohttp import web

from ..utils import _sanitize_name


async def _handle_marketplace_list(server, request) -> Any:
    """GET /api/marketplace/capsules -- lista capsulas en marketplace."""
    from zoe.marketplace import MarketplaceCatalog
    catalog = MarketplaceCatalog()
    capsules = catalog.list_capsules()
    return web.json_response({
        "capsules": [e.to_dict() for e in capsules],
        "count": len(capsules),
        "stats": catalog.get_stats(),
    })


async def _handle_marketplace_upload(server, request) -> Any:
    """POST /api/marketplace/upload -- sube capsula al marketplace."""
    from zoe.marketplace import MarketplaceCatalog, MarketplaceUploader

    data = await request.json()
    capsule_name = data.get("name")
    author = data.get("author", "anonymous")
    description = data.get("description", "")
    license_data = data.get("license", {"type": "free"})
    tags = data.get("tags", [])
    author_url = data.get("author_url")

    if not capsule_name:
        return web.json_response({"error": "name required"}, status=400)

    catalog = MarketplaceCatalog()
    capsules_dir = Path(__file__).resolve().parent.parent.parent / "capsules"
    use_cases_dir = Path(__file__).resolve().parent.parent.parent / "use_cases"
    uploader = MarketplaceUploader(catalog, capsules_dir, use_cases_dir)

    ok, message = uploader.upload_capsule(
        capsule_name=capsule_name,
        author=author,
        description=description,
        license_data=license_data,
        tags=tags,
        author_url=author_url,
    )

    return web.json_response({
        "success": ok,
        "name": capsule_name,
        "content_hash": message if ok else None,
        "error": None if ok else message,
    })


async def _handle_marketplace_download(server, request) -> Any:
    """POST /api/marketplace/download/{name} -- descarga e instala capsula."""
    from zoe.marketplace import MarketplaceCatalog, MarketplaceDownloader

    name = _sanitize_name(request.match_info["name"])
    catalog = MarketplaceCatalog()
    capsules_dir = Path(__file__).resolve().parent.parent.parent / "capsules"
    use_cases_dir = Path(__file__).resolve().parent.parent.parent / "use_cases"
    downloader = MarketplaceDownloader(catalog, capsules_dir, use_cases_dir)

    ok, message = downloader.download_capsule(name)
    return web.json_response({
        "success": ok,
        "name": name,
        "message": message,
    })


async def _handle_marketplace_use_cases(server, request) -> Any:
    """GET /api/marketplace/use_cases -- lista casos de uso en marketplace."""
    from zoe.marketplace import MarketplaceCatalog
    catalog = MarketplaceCatalog()
    use_cases = catalog.list_use_cases()
    return web.json_response({
        "use_cases": [e.to_dict() for e in use_cases],
        "count": len(use_cases),
    })


async def _handle_marketplace_upload_use_case(server, request) -> Any:
    """POST /api/marketplace/upload_use_case -- sube caso de uso al marketplace."""
    from zoe.marketplace import MarketplaceCatalog, MarketplaceUploader

    data = await request.json()
    use_case_name = data.get("name")
    author = data.get("author", "anonymous")
    description = data.get("description", "")
    license_data = data.get("license", {"type": "free"})
    tags = data.get("tags", [])

    if not use_case_name:
        return web.json_response({"error": "name required"}, status=400)

    catalog = MarketplaceCatalog()
    capsules_dir = Path(__file__).resolve().parent.parent.parent / "capsules"
    use_cases_dir = Path(__file__).resolve().parent.parent.parent / "use_cases"
    uploader = MarketplaceUploader(catalog, capsules_dir, use_cases_dir)

    ok, message = uploader.upload_use_case(
        use_case_name=use_case_name,
        author=author,
        description=description,
        license_data=license_data,
        tags=tags,
    )

    return web.json_response({
        "success": ok,
        "name": use_case_name,
        "content_hash": message if ok else None,
        "error": None if ok else message,
    })


