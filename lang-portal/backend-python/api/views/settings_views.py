import sqlite3
from pathlib import Path

from django.conf import settings

from api.models import StudySession, WordReviewItem
from api.utils import json_response

BASE_DIR = Path(settings.DATABASES["default"]["NAME"]).parent
MIGRATIONS_DIR = BASE_DIR / "Migrations"


def reset_history(request):
    deleted_review_items = WordReviewItem.objects.count()
    deleted_study_sessions = StudySession.objects.count()
    WordReviewItem.objects.all().delete()
    StudySession.objects.all().delete()

    return json_response(
        {
            "success": True,
            "message": "Study history has been reset",
            "deleted_study_sessions": deleted_study_sessions,
            "deleted_review_items": deleted_review_items,
        }
    )


def full_reset(request):
    # Note: For full reset, use command line: invoke full_reset
    # This endpoint is complex to implement due to database connection management
    return json_response(
        {
            "success": False,
            "message": "Please use command line 'invoke full_reset' for full database reset",
        },
        status=501
    )
