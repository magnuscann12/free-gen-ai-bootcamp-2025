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
    db_path = Path(settings.DATABASES["default"]["NAME"])

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    for filepath in migration_files:
        conn.executescript(filepath.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO schema_migrations (filename) VALUES (?)",
            (filepath.name,),
        )
    conn.commit()
    conn.close()

    from invoke import Context
    from tasks import seed_data

    seed_data(Context())

    return json_response(
        {
            "success": True,
            "message": "Database has been fully reset with seed data",
        }
    )
