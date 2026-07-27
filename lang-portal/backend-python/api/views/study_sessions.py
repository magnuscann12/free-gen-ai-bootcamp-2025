from django.utils import timezone

from api.models import StudySession, Word, WordReviewItem
from api.serializers import session_end_times, session_review_counts
from api.utils import (
    error_response,
    isoformat,
    json_response,
    paginate_queryset,
    paginated_response,
    parse_json_body,
    parse_page,
)


def _serialize_session_detail(session, end_times=None, review_counts=None):
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


def study_sessions_list(request):
    page = parse_page(request)
    if page is None:
        return error_response("Invalid page parameter", "validation_error", 400)

    queryset = (
        StudySession.objects.select_related("group", "study_activity")
        .order_by("-created_at")
    )
    sessions, pagination = paginate_queryset(queryset, page)
    session_ids = [s.id for s in sessions]
    end_times = session_end_times(session_ids)
    review_counts = session_review_counts(session_ids)
    items = [
        _serialize_session_detail(s, end_times, review_counts) for s in sessions
    ]
    return paginated_response(items, pagination)


def study_session_detail(request, session_id):
    try:
        session = StudySession.objects.select_related(
            "group", "study_activity"
        ).get(id=session_id)
    except StudySession.DoesNotExist:
        return error_response(
            "Study session not found", "study_session_not_found", 404
        )

    return json_response(_serialize_session_detail(session))


def study_session_words(request, session_id):
    if not StudySession.objects.filter(id=session_id).exists():
        return error_response(
            "Study session not found", "study_session_not_found", 404
        )

    page = parse_page(request)
    if page is None:
        return error_response("Invalid page parameter", "validation_error", 400)

    queryset = (
        WordReviewItem.objects.filter(study_session_id=session_id)
        .select_related("word")
        .order_by("created_at")
    )
    reviews, pagination = paginate_queryset(queryset, page)
    items = [
        {
            "word_id": r.word_id,
            "chinese": r.word.chinese,
            "pinyin": r.word.pinyin,
            "english": r.word.english,
            "correct": r.correct,
            "reviewed_at": isoformat(r.created_at),
        }
        for r in reviews
    ]
    return paginated_response(items, pagination)


def record_word_review(request, session_id, word_id):
    if not StudySession.objects.filter(id=session_id).exists():
        return error_response(
            "Study session not found", "study_session_not_found", 404
        )

    if not Word.objects.filter(id=word_id).exists():
        return error_response("Word not found", "word_not_found", 404)

    body = parse_json_body(request)
    if body is None:
        return error_response("Invalid JSON body", "validation_error", 400)

    correct = body.get("correct")
    if not isinstance(correct, bool):
        return error_response(
            "correct is required and must be a boolean", "validation_error", 400
        )

    review = WordReviewItem.objects.create(
        study_session_id=session_id,
        word_id=word_id,
        correct=correct,
        created_at=timezone.now(),
    )

    return json_response(
        {
            "id": review.id,
            "study_session_id": review.study_session_id,
            "word_id": review.word_id,
            "correct": review.correct,
            "created_at": isoformat(review.created_at),
        },
        status=201,
    )
