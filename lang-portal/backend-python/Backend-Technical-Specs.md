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
- The API will be built using
- The API will alaways return JSON
- There will be no authentication or authorization
- Everything will be treated as a single user

## Database Schema
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

## API Endpoints 

- GET /api/dashboard/last_study_session
- GET /api/dashboard/study_progress
- GET /api/dashboard/quick_stats
- GET /api/study_activities/:id
- GET /api/study_activities/:id/study_sessions

- POST /api/study_activities\
    -requires params: group_id, study_activity_id
- GET /api/words
    - Pagination with 100 items per page
- GET /api/groups
    - Pagination with 100 items per page

- GET /api/words
- GET /api/words/:id
- GET /api/groups
- GET /api/groups/:id
- GET /api/groups/:id/words
- GET /api/groups/:id/study_sessions
- GET /api/study_sessions
    -paginated with 100 items per page
- GET /api/study_session/:id
- GET /api/study_sessions/:id/words
- POST /api/reset_history
- POST /api/full_reset
- POST /api/study_session/:id/words/:word_id/review
    -requires params: correct