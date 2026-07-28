from django.urls import path

from api.views import dashboard, groups, settings_views, study_activities, study_sessions, words

urlpatterns = [
    path("dashboard/last_study_session", dashboard.last_study_session),
    path("dashboard/study_progress", dashboard.study_progress),
    path("dashboard/quick_stats", dashboard.quick_stats),
    path("study_activities", study_activities.study_activities_index),
    path("study_activities/<int:activity_id>", study_activities.study_activity_detail),
    path(
        "study_activities/<int:activity_id>/study_sessions",
        study_activities.study_activity_sessions,
    ),
    path("words", words.words_list),
    path("words/<int:word_id>", words.word_detail),
    path("groups", groups.groups_list),
    path("groups/<int:group_id>", groups.group_detail),
    path("groups/<int:group_id>/words", groups.group_words),
    path("groups/<int:group_id>/study_sessions", groups.group_study_sessions),
    path("study_sessions", study_sessions.study_sessions_list),
    path("study_sessions/<int:session_id>", study_sessions.study_session_detail),
    path(
        "study_sessions/<int:session_id>/words",
        study_sessions.study_session_words,
    ),
    path(
        "study_sessions/<int:session_id>/words/<int:word_id>/review",
        study_sessions.record_word_review,
    ),
    path("reset_history", settings_views.reset_history),
    path("full_reset", settings_views.full_reset),
]
