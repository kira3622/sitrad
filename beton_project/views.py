from django.http import HttpResponse, Http404
from django.conf import settings
from pathlib import Path


def _read_static_file(relative_path: str) -> bytes:
    base_static = Path(settings.BASE_DIR) / 'static'
    file_path = base_static / relative_path
    if not file_path.exists():
        raise Http404(f"Static file not found: {relative_path}")
    return file_path.read_bytes()


def service_worker(request):
    """Expose service-worker.js at root for Web Push."""
    content = _read_static_file('service-worker.js')
    return HttpResponse(content, content_type='application/javascript')


def push_test_page(request):
    """Simple page to test Web Push subscription."""
    content = _read_static_file('push-test.html')
    return HttpResponse(content, content_type='text/html; charset=utf-8')