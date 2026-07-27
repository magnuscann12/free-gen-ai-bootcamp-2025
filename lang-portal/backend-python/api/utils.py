import json
import math

from django.http import JsonResponse

PER_PAGE = 100


def json_response(data, status=200):
    return JsonResponse(data, status=status, safe=isinstance(data, dict))


def error_response(message, code, status):
    return json_response({"error": message, "code": code}, status=status)


def parse_page(request):
    page_param = request.GET.get("page", "1")
    try:
        page = int(page_param)
    except (TypeError, ValueError):
        return None
    if page < 1:
        return None
    return page


def paginate_queryset(queryset, page):
    total_items = queryset.count()
    total_pages = max(1, math.ceil(total_items / PER_PAGE)) if total_items else 1
    if page > total_pages and total_items > 0:
        page = total_pages
    offset = (page - 1) * PER_PAGE
    items = list(queryset[offset : offset + PER_PAGE])
    return items, {
        "page": page,
        "per_page": PER_PAGE,
        "total_items": total_items,
        "total_pages": total_pages if total_items else 1,
    }


def paginated_response(items, pagination):
    return json_response({"items": items, "pagination": pagination})


def parse_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None


def isoformat(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.isoformat() + "Z"
    return dt.isoformat().replace("+00:00", "Z")
