# Backend Server Technical Specifications

## Business Goal:
A language learning school wants to build a prototype of learning portal which will act as three
things:
-  Inventory of possible vocabulary that can be learned
-  Act as a Learning record store (LRS), providing correct and wrong score on practice vocabulary
- A unified launchpad to launch different learning apps

## Technical Requirements
- The backend will be built using python
- The database will be SQLite3
- The API will be built using Django
- The API will alaways return JSON
- There will be no authentication or authorization
- Everything will be treated as a single user

## Database Schema
Our database will be a single sqlite database called 'words.db' that will be in the root of the project folder of 'backend-python'

We will have the following tables
- words : Stored vocabulary words
    - id integer
    - chinese string
    - pinyin string
    - english string
    - parts json
- word_groups : join table for word and group many to many
    -id integer
    - word_id integer
    - group_id integer
- groups : thematic group of words
    - id integer
    - name string
- study_sessions : records of study sessions grouping word_review_items
    -id integer
    - group_id integer
    - study_activity_id integer
    - created_at datetime
- study_activities : a specific study activity, linking a study session to group
    - id integer
    - study_session_id integer
    - group_id integer
    - created_at datetime
- word_review_items : a record of word practice, determining if the word is correct or wrong
    - word_id integer
    - study_session_id integer
    - correct boolean
    - created_at datetime

## API Conventions

- All endpoints return `Content-Type: application/json`.
- Paginated list endpoints accept an optional query param `page` (default: `1`, 100 items per page).
- Error responses use a consistent shape:

```json
{
  "error": "Human-readable message",
  "code": "machine_readable_code"
}
```

Common HTTP status codes:
- `200` — success (GET, POST mutations that return data)
- `201` — resource created (POST)
- `400` — invalid request body or query params
- `404` — resource not found
- `500` — server error

### Shared pagination object

All paginated responses include:

```json
{
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total_items": 124,
    "total_pages": 2
  }
}
```

---

## API Endpoints

### Dashboard

#### GET /api/dashboard/last_study_session

Returns the most recent study session summary for the dashboard "Last Study Session" card.

**Query params:** none

**Response `200` — session exists:**

```json
{
  "study_session_id": 12,
  "activity_id": 1,
  "activity_name": "Flashcards",
  "group_id": 3,
  "group_name": "Basic Greetings",
  "created_at": "2026-07-22T14:30:00Z",
  "correct_count": 8,
  "wrong_count": 2
}
```

**Response `200` — no sessions yet:**

```json
null
```

---

#### GET /api/dashboard/study_progress

Returns vocabulary coverage and mastery for the dashboard "Study Progress" card.

**Query params:** none

**Response `200`:**

```json
{
  "words_studied": 3,
  "total_words": 124,
  "mastery_percentage": 2.4
}
```

| Field | Type | Description |
|-------|------|-------------|
| `words_studied` | integer | Distinct words that have at least one `word_review_item` |
| `total_words` | integer | Total rows in `words` |
| `mastery_percentage` | float | `(words with more correct than wrong reviews / total_words) * 100`, rounded to 1 decimal |

---

#### GET /api/dashboard/quick_stats

Returns aggregate stats for the dashboard "Quick Stats" card.

**Query params:** none

**Response `200`:**

```json
{
  "success_rate_percentage": 80.0,
  "total_study_sessions": 4,
  "total_active_groups": 3,
  "study_streak_days": 4
}
```

| Field | Type | Description |
|-------|------|-------------|
| `success_rate_percentage` | float | `(correct reviews / total reviews) * 100` across all time |
| `total_study_sessions` | integer | Count of rows in `study_sessions` |
| `total_active_groups` | integer | Distinct `group_id` values that appear in at least one `study_session` |
| `study_streak_days` | integer | Consecutive calendar days (including today) with at least one review item |

---

### Study Activities

> **Note:** The frontend also needs `GET /api/study_activities` (index of all activity types). Add that endpoint when implementing the Study Activities index page.

#### GET /api/study_activities/:id

Returns metadata for a single study activity type (name, thumbnail, description).

**Path params:** `id` — activity type id

**Response `200`:**

```json
{
  "id": 1,
  "name": "Flashcards",
  "thumbnail_url": "/static/images/flashcards.png",
  "description": "Practice vocabulary with flip cards.",
  "launch_url": "https://example.com/flashcards"
}
```

**Response `404`:**

```json
{
  "error": "Study activity not found",
  "code": "study_activity_not_found"
}
```

---

#### GET /api/study_activities/:id/study_sessions

Returns paginated past study sessions for this activity type.

**Path params:** `id` — activity type id  
**Query params:** `page` (optional, default `1`)

**Response `200`:**

```json
{
  "items": [
    {
      "id": 12,
      "group_id": 3,
      "group_name": "Basic Greetings",
      "start_time": "2026-07-22T14:30:00Z",
      "end_time": "2026-07-22T14:45:00Z",
      "review_items_count": 10
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total_items": 5,
    "total_pages": 1
  }
}
```

| Item field | Type | Description |
|------------|------|-------------|
| `start_time` | string (ISO 8601) | `study_sessions.created_at` |
| `end_time` | string (ISO 8601) \| null | Timestamp of the last `word_review_item` for this session; `null` if no reviews yet |
| `review_items_count` | integer | Count of `word_review_items` for this session |

---

#### POST /api/study_activities

Creates a new study session for the given group and activity type. Used by the launch form.

**Request body (JSON):**

```json
{
  "group_id": 3,
  "study_activity_id": 1
}
```

**Response `201`:**

```json
{
  "study_session_id": 13,
  "study_activity_id": 1,
  "group_id": 3,
  "created_at": "2026-07-23T16:00:00Z"
}
```

**Response `400` — missing or invalid fields:**

```json
{
  "error": "group_id and study_activity_id are required",
  "code": "validation_error"
}
```

---

### Words

#### GET /api/words

Returns a paginated list of all vocabulary words with lifetime review stats.

**Query params:** `page` (optional, default `1`)

**Response `200`:**

```json
{
  "items": [
    {
      "id": 1,
      "chinese": "你好",
      "pinyin": "nǐ hǎo",
      "english": "hello",
      "correct_count": 5,
      "wrong_count": 2
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total_items": 124,
    "total_pages": 2
  }
}
```

---

#### GET /api/words/:id

Returns full detail for a single word, including groups it belongs to.

**Path params:** `id` — word id

**Response `200`:**

```json
{
  "id": 1,
  "chinese": "你好",
  "pinyin": "nǐ hǎo",
  "english": "hello",
  "parts": {
    "radical": "亻",
    "stroke_count": 7
  },
  "correct_count": 5,
  "wrong_count": 2,
  "groups": [
    {
      "id": 3,
      "name": "Basic Greetings"
    }
  ]
}
```

**Response `404`:**

```json
{
  "error": "Word not found",
  "code": "word_not_found"
}
```

---

### Groups

#### GET /api/groups

Returns a paginated list of word groups with word counts.

**Query params:** `page` (optional, default `1`)

**Response `200`:**

```json
{
  "items": [
    {
      "id": 3,
      "name": "Basic Greetings",
      "word_count": 15
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total_items": 8,
    "total_pages": 1
  }
}
```

---

#### GET /api/groups/:id

Returns group name and statistics for the group show page header.

**Path params:** `id` — group id

**Response `200`:**

```json
{
  "id": 3,
  "name": "Basic Greetings",
  "word_count": 15
}
```

**Response `404`:**

```json
{
  "error": "Group not found",
  "code": "group_not_found"
}
```

---

#### GET /api/groups/:id/words

Returns a paginated list of words in the group (same item shape as `GET /api/words`).

**Path params:** `id` — group id  
**Query params:** `page` (optional, default `1`)

**Response `200`:**

```json
{
  "items": [
    {
      "id": 1,
      "chinese": "你好",
      "pinyin": "nǐ hǎo",
      "english": "hello",
      "correct_count": 5,
      "wrong_count": 2
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total_items": 15,
    "total_pages": 1
  }
}
```

---

#### GET /api/groups/:id/study_sessions

Returns a paginated list of study sessions for this group (same item shape as `GET /api/study_sessions`).

**Path params:** `id` — group id  
**Query params:** `page` (optional, default `1`)

**Response `200`:**

```json
{
  "items": [
    {
      "id": 12,
      "activity_id": 1,
      "activity_name": "Flashcards",
      "group_id": 3,
      "group_name": "Basic Greetings",
      "start_time": "2026-07-22T14:30:00Z",
      "end_time": "2026-07-22T14:45:00Z",
      "review_items_count": 10
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total_items": 2,
    "total_pages": 1
  }
}
```

---

### Study Sessions

> **Path naming note:** The spec originally mixed `/api/study_session/:id` (singular) and `/api/study_sessions/:id/words` (plural). Use **`/api/study_sessions/:id`** consistently for the show endpoint.

#### GET /api/study_sessions

Returns a paginated list of all study sessions.

**Query params:** `page` (optional, default `1`)

**Response `200`:**

```json
{
  "items": [
    {
      "id": 12,
      "activity_id": 1,
      "activity_name": "Flashcards",
      "group_id": 3,
      "group_name": "Basic Greetings",
      "start_time": "2026-07-22T14:30:00Z",
      "end_time": "2026-07-22T14:45:00Z",
      "review_items_count": 10
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total_items": 4,
    "total_pages": 1
  }
}
```

---

#### GET /api/study_sessions/:id

Returns detail for a single study session.

**Path params:** `id` — study session id

**Response `200`:**

```json
{
  "id": 12,
  "activity_id": 1,
  "activity_name": "Flashcards",
  "group_id": 3,
  "group_name": "Basic Greetings",
  "start_time": "2026-07-22T14:30:00Z",
  "end_time": "2026-07-22T14:45:00Z",
  "review_items_count": 10
}
```

**Response `404`:**

```json
{
  "error": "Study session not found",
  "code": "study_session_not_found"
}
```

---

#### GET /api/study_sessions/:id/words

Returns a paginated list of word review items recorded during this session.

**Path params:** `id` — study session id  
**Query params:** `page` (optional, default `1`)

**Response `200`:**

```json
{
  "items": [
    {
      "word_id": 1,
      "chinese": "你好",
      "pinyin": "nǐ hǎo",
      "english": "hello",
      "correct": true,
      "reviewed_at": "2026-07-22T14:32:00Z"
    },
    {
      "word_id": 2,
      "chinese": "谢谢",
      "pinyin": "xiè xie",
      "english": "thank you",
      "correct": false,
      "reviewed_at": "2026-07-22T14:33:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 100,
    "total_items": 10,
    "total_pages": 1
  }
}
```

---

#### POST /api/study_sessions/:id/words/:word_id/review

Records a single word review during an active study session. Called by external learning apps.

**Path params:** `id` — study session id, `word_id` — word id

**Request body (JSON):**

```json
{
  "correct": true
}
```

**Response `201`:**

```json
{
  "id": 99,
  "study_session_id": 12,
  "word_id": 1,
  "correct": true,
  "created_at": "2026-07-23T16:05:00Z"
}
```

**Response `400` — missing `correct`:**

```json
{
  "error": "correct is required and must be a boolean",
  "code": "validation_error"
}
```

**Response `404` — session or word not found:**

```json
{
  "error": "Study session not found",
  "code": "study_session_not_found"
}
```

---

### Settings

#### POST /api/reset_history

Deletes all study sessions and word review items. Vocabulary and groups are kept.

**Request body:** none (empty `{}` is fine)

**Response `200`:**

```json
{
  "success": true,
  "message": "Study history has been reset",
  "deleted_study_sessions": 4,
  "deleted_review_items": 42
}
```

---

#### POST /api/full_reset

Drops all tables, re-creates schema, and re-seeds initial data.

**Request body:** none (empty `{}` is fine)

**Response `200`:**

```json
{
  "success": true,
  "message": "Database has been fully reset with seed data"
}
```

## Invoke Tasks
Invoke is a task runner for Python
Lets list our possible tasks for our langportal

### Initialise Database
This task will initialize sqlite database

### Migrate Database
This task will run a series of migrations sql files on the database
Migrations live in the 'Migrations' folder
The migration files will run in order of their file names
The file name should look like thsi

```sql
0001_init.sql
0002_create_words_table.sql
```

### Seed data 
This will import JSON files and transform them into target data for our database

All seeds files live in the 'seeds' folder
All seed files should be loaded
In our task we should have DSL to specific each seed file and its expected group word name


 ```json
[
    {
      "chinese": "你好",
      "pinyin": "nǐ hǎo",
      "english": "hello"
    }
]
```