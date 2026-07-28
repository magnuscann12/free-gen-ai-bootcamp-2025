## Test API Endpoints

If you want to test the API endpoints, run:

```powershell
python test_api.py
```
## Kill if already running

If you want to kill the server if it's already running, run:

```powershell
netstat -ano | findstr :8000
taskkill /F /PID <PID_from_above>
```
## Run Server
If you want to run the server, run:

```powershell
python manage.py runserver
```

## API Endpoints

### Dashboard
- `GET /api/dashboard/last_study_session` → `dashboard.last_study_session`
- `GET /api/dashboard/study_progress` → `dashboard.study_progress`
- `GET /api/dashboard/quick_stats` → `dashboard.quick_stats`

### Words
- `GET /api/words` → `words.words_list`
- `GET /api/words/:id` → `words.word_detail`

### Groups
- `GET /api/groups` → `groups.groups_list`
- `GET /api/groups/:id` → `groups.group_detail`
- `GET /api/groups/:id/words` → `groups.group_words`
- `GET /api/groups/:id/study_sessions` → `groups.group_study_sessions`

### Study Activities
- `GET /api/study_activities` → `study_activities.study_activities_index`
- `POST /api/study_activities` → `study_activities.create_study_session`
- `GET /api/study_activities/:id` → `study_activities.study_activity_detail`
- `GET /api/study_activities/:id/study_sessions` → `study_activities.study_activity_sessions`

### Study Sessions
- `GET /api/study_sessions` → `study_sessions.study_sessions_list`
- `GET /api/study_sessions/:id` → `study_sessions.study_session_detail`
- `GET /api/study_sessions/:id/words` → `study_sessions.study_session_words`
- `POST /api/study_sessions/:id/words/:word_id/review` → `study_sessions.record_word_review`

### Settings
- `POST /api/reset_history` → `settings_views.reset_history`
- `POST /api/full_reset` → `settings_views.full_reset` (returns 501 - use CLI instead)