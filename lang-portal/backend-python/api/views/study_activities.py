from django.utils import timezone

from api.models import Group, StudyActivity, StudySession, Word, WordReviewItem
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


def study_activities_index(request):
    if request.method == "POST":
        return create_study_session(request)

    activities = StudyActivity.objects.all().order_by("id")
    items = [
        {
            "id": a.id,
            "name": a.name,
            "thumbnail_url": a.thumbnail_url,
            "description": a.description,
            "launch_url": a.launch_url,
        }
        for a in activities
    ]
    return json_response({"items": items})


def study_activity_detail(request, activity_id):
    try:
        activity = StudyActivity.objects.get(id=activity_id)
    except StudyActivity.DoesNotExist:
        return error_response(
            "Study activity not found", "study_activity_not_found", 404
        )

    return json_response(
        {
            "id": activity.id,
            "name": activity.name,
            "thumbnail_url": activity.thumbnail_url,
            "description": activity.description,
            "launch_url": activity.launch_url,
        }
    )


def study_activity_sessions(request, activity_id):
    if not StudyActivity.objects.filter(id=activity_id).exists():
        return error_response(
            "Study activity not found", "study_activity_not_found", 404
        )

    page = parse_page(request)
    if page is None:
        return error_response("Invalid page parameter", "validation_error", 400)

    queryset = (
        StudySession.objects.filter(study_activity_id=activity_id)
        .select_related("group")
        .order_by("-created_at")
    )
    sessions, pagination = paginate_queryset(queryset, page)
    session_ids = [s.id for s in sessions]
    end_times = session_end_times(session_ids)
    review_counts = session_review_counts(session_ids)

    items = [
        {
            "id": s.id,
            "group_id": s.group_id,
            "group_name": s.group.name,
            "start_time": isoformat(s.created_at),
            "end_time": isoformat(end_times.get(s.id)),
            "review_items_count": review_counts.get(s.id, 0),
        }
        for s in sessions
    ]
    return paginated_response(items, pagination)


def create_study_session(request):
    body = parse_json_body(request)
    if body is None:
        return error_response("Invalid JSON body", "validation_error", 400)

    group_id = body.get("group_id")
    study_activity_id = body.get("study_activity_id")

    if group_id is None or study_activity_id is None:
        return error_response(
            "group_id and study_activity_id are required", "validation_error", 400
        )

    try:
        group_id = int(group_id)
        study_activity_id = int(study_activity_id)
    except (TypeError, ValueError):
        return error_response(
            "group_id and study_activity_id are required", "validation_error", 400
        )

    if not Group.objects.filter(id=group_id).exists():
        return error_response("Group not found", "group_not_found", 404)

    if not StudyActivity.objects.filter(id=study_activity_id).exists():
        return error_response(
            "Study activity not found", "study_activity_not_found", 404
        )

    session = StudySession.objects.create(
        group_id=group_id,
        study_activity_id=study_activity_id,
        created_at=timezone.now(),
    )

    return json_response(
        {
            "study_session_id": session.id,
            "study_activity_id": session.study_activity_id,
            "group_id": session.group_id,
            "created_at": isoformat(session.created_at),
        },
        status=201,
    )
