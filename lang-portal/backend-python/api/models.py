import json

from django.db import models


class Word(models.Model):
    chinese = models.TextField()
    pinyin = models.TextField()
    english = models.TextField()
    parts = models.TextField(default="{}")

    class Meta:
        managed = False
        db_table = "words"

    @property
    def parts_dict(self):
        try:
            return json.loads(self.parts)
        except (json.JSONDecodeError, TypeError):
            return {}


class Group(models.Model):
    name = models.TextField(unique=True)

    class Meta:
        managed = False
        db_table = "groups"


class WordGroup(models.Model):
    word = models.ForeignKey(Word, on_delete=models.DO_NOTHING, db_column="word_id")
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, db_column="group_id")

    class Meta:
        managed = False
        db_table = "word_groups"


class StudyActivity(models.Model):
    name = models.TextField()
    thumbnail_url = models.TextField()
    description = models.TextField()
    launch_url = models.TextField()

    class Meta:
        managed = False
        db_table = "study_activities"


class StudySession(models.Model):
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING, db_column="group_id")
    study_activity = models.ForeignKey(
        StudyActivity, on_delete=models.DO_NOTHING, db_column="study_activity_id"
    )
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "study_sessions"


class WordReviewItem(models.Model):
    word = models.ForeignKey(Word, on_delete=models.DO_NOTHING, db_column="word_id")
    study_session = models.ForeignKey(
        StudySession, on_delete=models.DO_NOTHING, db_column="study_session_id"
    )
    correct = models.BooleanField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "word_review_items"
