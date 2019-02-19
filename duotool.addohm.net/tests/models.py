from django.db import models


class TestAnswers(models.Model):
    phraseid = models.IntegerField(unique=True, blank=True, null=True)
    question = models.TextField(blank=True, null=True)
    answer = models.CharField(max_length=50, blank=True, null=True)
