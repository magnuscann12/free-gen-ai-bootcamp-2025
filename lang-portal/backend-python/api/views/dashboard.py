from datetime import timedelta

from django.utils import timezone

from api.models import StudySession, Word, WordReviewItem
from api.utils import isoformat, json_response


def last_study_session(request):
    session = (
        StudySession.objects.select_related("group", "study_activity")
        .order_by("-created_at")
        .first()
    )
    if session is None:
        return json_response(None)

    correct_count = WordReviewItem.objects.filter(
        study_session_id=session.id, correct=True
    ).count()
    wrong_count = WordReviewItem.objects.filter(
        study_session_id=session.id, correct=False
    ).count()

    return json_response(
        {
            "study_session_id": session.id,
            "activity_id": session.study_activity_id,
            "activity_name": session.study_activity.name,
            "group_id": session.group_id,
            "group_name": session.group.name,
            "created_at": isoformat(session.created_at),
            "correct_count": correct_count,
            "wrong_count": wrong_count,
        }
    )


def study_progress(request):
    total_words = Word.objects.count()
    studied_word_ids = WordReviewItem.objects.values_list("word_id", flat=True).distinct()
    words_studied = len(set(studied_word_ids))

    mastered = 0
    for word_id in set(studied_word_ids):
        correct = WordReviewItem.objects.filter(word_id=word_id, correct=True).count()
        wrong = WordReviewItem.objects.filter(word_id=word_id, correct=False).count()
        if correct > wrong:
            mastered += 1

    mastery_percentage = round((mastered / total_words) * 100, 1) if total_words else 0.0

    return json_response(
        {
            "words_studied": words_studied,
            "total_words": total_words,
            "mastery_percentage": mastery_percentage,
        }
    )


def _study_streak_days():
    review_dates = (
        WordReviewItem.objects.values_list("created_at", flat=True)
        .order_by("-created_at")
    )
    if not review_dates:
        return 0

    days_with_reviews = set()
    for dt in review_dates:
        if dt.tzinfo is None:
            days_with_reviews.add(dt.date())
        else:
            days_with_reviews.add(timezone.localdate(dt))

    streak = 0
    current_day = timezone.localdate()
    while current_day in days_with_reviews:
        streak += 1
        current_day -= timedelta(days=1)

    return streak


def quick_stats(request):
    total_reviews = WordReviewItem.objects.count()
    correct_reviews = WordReviewItem.objects.filter(correct=True).count()
    success_rate = (
        round((correct_reviews / total_reviews) * 100, 1) if total_reviews else 0.0
    )

    total_study_sessions = StudySession.objects.count()
    total_active_groups = (
        StudySession.objects.values("group_id").distinct().count()
    )

    return json_response(
        {
            "success_rate_percentage": success_rate,
            "total_study_sessions": total_study_sessions,
            "total_active_groups": total_active_groups,
            "study_streak_days": _study_streak_days(),
        }
    )
