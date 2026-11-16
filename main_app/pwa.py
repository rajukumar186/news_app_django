import json
from pathlib import Path

from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import FileResponse, HttpResponse


def web_manifest(request):
    manifest = {
        "id": "/",
        "name": "The People's Era - World News",
        "short_name": "People's Era",
        "description": "News, weather, and market updates from The People's Era.",
        "start_url": "/",
        "scope": "/",
        "display": "standalone",
        "background_color": "#0b1120",
        "theme_color": "#b40a0a",
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": staticfiles_storage.url("pwa/app-icon.svg"),
                "sizes": "any",
                "type": "image/svg+xml",
                "purpose": "any maskable",
            }
        ],
    }
    return HttpResponse(
        json.dumps(manifest),
        content_type="application/manifest+json",
    )


def service_worker(request):
    worker_path = Path(__file__).resolve().parent / "static" / "pwa" / "service-worker.js"
    response = FileResponse(worker_path.open("rb"), content_type="application/javascript")
    response["Cache-Control"] = "no-cache"
    response["Service-Worker-Allowed"] = "/"
    return response
