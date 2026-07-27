import json
import sqlite3
from pathlib import Path

from invoke import task

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "words.db"
MIGRATIONS_DIR = BASE_DIR / "Migrations"
SEEDS_DIR = BASE_DIR / "seeds"

SEED_CONFIG = [
    {"file": "basic_greetings.json", "group_name": "Basic Greetings"},
    {"file": "numbers.json", "group_name": "Numbers"},
]

STUDY_ACTIVITIES = [
    {
        "name": "Flashcards",
        "thumbnail_url": "/static/images/flashcards.png",
        "description": "Practice vocabulary with flip cards.",
        "launch_url": "https://example.com/flashcards",
    },
    {
        "name": "Typing Tutor",
        "thumbnail_url": "/static/images/typing.png",
        "description": "Practice typing Chinese characters.",
        "launch_url": "https://example.com/typing",
    },
]


def _connect():
    return sqlite3.connect(DB_PATH)


def _run_sql_file(conn, filepath: Path):
    sql = filepath.read_text(encoding="utf-8")
    conn.executescript(sql)


@task
def init_db(c):
    """Initialize the SQLite database file."""
    if DB_PATH.exists():
        print(f"Database already exists at {DB_PATH}")
        return
    conn = _connect()
    conn.close()
    print(f"Created database at {DB_PATH}")


@task
def migrate_db(c):
    """Run pending SQL migrations in filename order."""
    if not DB_PATH.exists():
        init_db(c)

    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            applied_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()

    applied = {
        row[0]
        for row in conn.execute("SELECT filename FROM schema_migrations").fetchall()
    }

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migration_files:
        print("No migration files found.")
        conn.close()
        return

    for filepath in migration_files:
        if filepath.name in applied:
            print(f"Skipping {filepath.name} (already applied)")
            continue
        print(f"Applying {filepath.name}...")
        _run_sql_file(conn, filepath)
        conn.execute(
            "INSERT INTO schema_migrations (filename) VALUES (?)",
            (filepath.name,),
        )
        conn.commit()
        print(f"Applied {filepath.name}")

    conn.close()
    print("Migrations complete.")


def _seed_study_activities(conn):
    count = conn.execute("SELECT COUNT(*) FROM study_activities").fetchone()[0]
    if count > 0:
        return

    for activity in STUDY_ACTIVITIES:
        conn.execute(
            """
            INSERT INTO study_activities (name, thumbnail_url, description, launch_url)
            VALUES (?, ?, ?, ?)
            """,
            (
                activity["name"],
                activity["thumbnail_url"],
                activity["description"],
                activity["launch_url"],
            ),
        )


def _seed_words_for_group(conn, seed_file: str, group_name: str):
    filepath = SEEDS_DIR / seed_file
    if not filepath.exists():
        print(f"Warning: seed file not found: {filepath}")
        return

    group_row = conn.execute(
        "SELECT id FROM groups WHERE name = ?", (group_name,)
    ).fetchone()
    if group_row:
        group_id = group_row[0]
    else:
        cursor = conn.execute(
            "INSERT INTO groups (name) VALUES (?)", (group_name,)
        )
        group_id = cursor.lastrowid

    words = json.loads(filepath.read_text(encoding="utf-8"))
    for word in words:
        parts = json.dumps(word.get("parts", {}), ensure_ascii=False)
        existing = conn.execute(
            """
            SELECT id FROM words
            WHERE chinese = ? AND pinyin = ? AND english = ?
            """,
            (word["chinese"], word["pinyin"], word["english"]),
        ).fetchone()

        if existing:
            word_id = existing[0]
        else:
            cursor = conn.execute(
                """
                INSERT INTO words (chinese, pinyin, english, parts)
                VALUES (?, ?, ?, ?)
                """,
                (word["chinese"], word["pinyin"], word["english"], parts),
            )
            word_id = cursor.lastrowid

        conn.execute(
            """
            INSERT OR IGNORE INTO word_groups (word_id, group_id)
            VALUES (?, ?)
            """,
            (word_id, group_id),
        )


@task
def seed_data(c):
    """Load seed JSON files into the database."""
    if not DB_PATH.exists():
        migrate_db(c)
    else:
        conn_check = _connect()
        tables = conn_check.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn_check.close()
        if not tables:
            migrate_db(c)

    conn = _connect()
    _seed_study_activities(conn)

    for entry in SEED_CONFIG:
        print(f"Seeding {entry['file']} -> {entry['group_name']}")
        _seed_words_for_group(conn, entry["file"], entry["group_name"])

    conn.commit()
    conn.close()
    print("Seed data loaded.")


@task
def setup(c):
    """Initialize database, run migrations, and seed data."""
    init_db(c)
    migrate_db(c)
    seed_data(c)


@task
def reset_history(c):
    """Delete all study sessions and word review items."""
    if not DB_PATH.exists():
        print("Database does not exist.")
        return

    conn = _connect()
    review_count = conn.execute("SELECT COUNT(*) FROM word_review_items").fetchone()[0]
    session_count = conn.execute("SELECT COUNT(*) FROM study_sessions").fetchone()[0]
    conn.execute("DELETE FROM word_review_items")
    conn.execute("DELETE FROM study_sessions")
    conn.commit()
    conn.close()
    print(f"Deleted {session_count} study sessions and {review_count} review items.")


@task
def full_reset(c):
    """Drop all data and re-run migrations and seeds."""
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"Removed {DB_PATH}")
    setup(c)
