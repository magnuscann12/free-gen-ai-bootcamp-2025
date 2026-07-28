from django.db.models import Count

from api.models import Group, StudySession, Word, WordGroup
from api.serializers import (
    serialize_word_summary,
    session_end_times,
    session_review_counts,
    word_review_counts,
)
from api.utils import (
    error_response,
    isoformat,
    paginate_queryset,
    paginated_response,
    parse_page,
    json_response,
)


def _serialize_session(session, end_times=None, review_counts=None):
    if end_times is None:
        end_times = session_end_times([session.id])
    if review_counts is None:
        review_counts = session_review_counts([session.id])

    return {
        "id": session.id,
        "activity_id": session.study_activity_id,
        "activity_name": session.study_activity.name,
        "group_id": session.group_id,
        "group_name": session.group.name,
        "start_time": isoformat(session.created_at),
        "end_time": isoformat(end_times.get(session.id)),
        "review_items_count": review_counts.get(session.id, 0),
    }


def groups_list(request):
    page = parse_page(request)
    if page is None:
        return error_response("Invalid page parameter", "validation_error", 400)

    queryset = Group.objects.annotate(word_count=Count("wordgroup")).order_by("id")
    groups, pagination = paginate_queryset(queryset, page)
    items = [
        {"id": g.id, "name": g.name, "word_count": g.word_count}
        for g in groups
    ]
    return paginated_response(items, pagination)


def group_detail(request, group_id):
    try:
        group = Group.objects.annotate(word_count=Count("wordgroup")).get(id=group_id)
    except Group.DoesNotExist:
        return error_response("Group not found", "group_not_found", 404)

    return json_response(
        {"id": group.id, "name": group.name, "word_count": group.word_count}
    )


def group_words(request, group_id):
    if not Group.objects.filter(id=group_id).exists():
        return error_response("Group not found", "group_not_found", 404)

    page = parse_page(request)
    if page is None:
        return error_response("Invalid page parameter", "validation_error", 400)

    word_ids = WordGroup.objects.filter(group_id=group_id).values_list(
        "word_id", flat=True
    )
    queryset = Word.objects.filter(id__in=word_ids).order_by("id")
    words, pagination = paginate_queryset(queryset, page)
    counts = word_review_counts([w.id for w in words])
    items = [serialize_word_summary(w, counts) for w in words]
    return paginated_response(items, pagination)


def group_study_sessions(request, group_id):
    if not Group.objects.filter(id=group_id).exists():
        return error_response("Group not found", "group_not_found", 404)

    page = parse_page(request)
    if page is None:
        return error_response("Invalid page parameter", "validation_error", 400)

    queryset = (
        StudySession.objects.filter(group_id=group_id)
        .select_related("group", "study_activity")
        .order_by("-created_at")
    )
    sessions, pagination = paginate_queryset(queryset, page)
    session_ids = [s.id for s in sessions]
    end_times = session_end_times(session_ids)
    review_counts = session_review_counts(session_ids)
    items = [
        _serialize_session(s, end_times, review_counts) for s in sessions
    ]
    return paginated_response(items, pagination)
