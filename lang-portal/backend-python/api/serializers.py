from django.db.models import Count, Max, Q

from api.models import Group, Word, WordGroup, WordReviewItem


def word_review_counts(word_ids=None):
    """Return {word_id: {'correct': n, 'wrong': n}} for optional word id filter."""
    qs = WordReviewItem.objects.values("word_id").annotate(
        correct_count=Count("id", filter=Q(correct=True)),
        wrong_count=Count("id", filter=Q(correct=False)),
    )
    if word_ids is not None:
        qs = qs.filter(word_id__in=word_ids)

    return {
        row["word_id"]: {
            "correct_count": row["correct_count"],
            "wrong_count": row["wrong_count"],
        }
        for row in qs
    }


def serialize_word_summary(word, counts=None):
    if counts is None:
        counts = word_review_counts([word.id]).get(
            word.id, {"correct_count": 0, "wrong_count": 0}
        )
    else:
        counts = counts.get(word.id, {"correct_count": 0, "wrong_count": 0})

    return {
        "id": word.id,
        "chinese": word.chinese,
        "pinyin": word.pinyin,
        "english": word.english,
        "correct_count": counts["correct_count"],
        "wrong_count": counts["wrong_count"],
    }


def serialize_word_detail(word):
    counts = word_review_counts([word.id]).get(
        word.id, {"correct_count": 0, "wrong_count": 0}
    )
    group_ids = WordGroup.objects.filter(word_id=word.id).values_list(
        "group_id", flat=True
    )
    groups = [
        {"id": g.id, "name": g.name}
        for g in Group.objects.filter(id__in=group_ids).order_by("name")
    ]
    return {
        **serialize_word_summary(word, {word.id: counts}),
        "parts": word.parts_dict,
        "groups": groups,
    }


def session_end_times(session_ids):
    rows = (
        WordReviewItem.objects.filter(study_session_id__in=session_ids)
        .values("study_session_id")
        .annotate(end_time=Max("created_at"))
    )
    return {row["study_session_id"]: row["end_time"] for row in rows}


def session_review_counts(session_ids):
    rows = (
        WordReviewItem.objects.filter(study_session_id__in=session_ids)
        .values("study_session_id")
        .annotate(review_items_count=Count("id"))
    )
    return {row["study_session_id"]: row["review_items_count"] for row in rows}
