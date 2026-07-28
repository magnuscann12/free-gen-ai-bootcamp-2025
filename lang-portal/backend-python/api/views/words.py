from api.models import Word
from api.serializers import serialize_word_summary, word_review_counts
from api.utils import (
    error_response,
    paginate_queryset,
    paginated_response,
    parse_page,
    json_response,
)


def words_list(request):
    page = parse_page(request)
    if page is None:
        return error_response("Invalid page parameter", "validation_error", 400)

    queryset = Word.objects.all().order_by("id")
    words, pagination = paginate_queryset(queryset, page)
    word_ids = [w.id for w in words]
    counts = word_review_counts(word_ids)
    items = [serialize_word_summary(w, counts) for w in words]
    return paginated_response(items, pagination)


def word_detail(request, word_id):
    try:
        word = Word.objects.get(id=word_id)
    except Word.DoesNotExist:
        return error_response("Word not found", "word_not_found", 404)

    from api.serializers import serialize_word_detail

    return json_response(serialize_word_detail(word))
