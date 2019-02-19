"""
Combine the data from cedict and hanzidb to create:
    class Phrases(models.Model):
        traditional = models.CharField(max_length = 20)
        simplified = models.CharField(max_length = 20)
        radical = models.CharField(max_length = 20)
        pinyin = models.CharField(max_length = 255)
        hsk_level = models.IntegerField
        frequency_rank = models.IntegerField
        phrase_url = models.URLField
        radical_url = models.URLField
        definition = models.TextField()
"""
from django.db import models


class HanDictionary(models.Model):
    traditional = models.CharField(max_length=20)
    simplified = models.CharField(max_length=20)
    pinyin = models.CharField(max_length=255)
    simplified_radical = models.CharField(max_length=20)
    hsk_level = models.IntegerField(blank=True, null=True)
    frequency_rank = models.IntegerField(blank=True, null=True)
    phrase_url = models.URLField()
    radical_url = models.URLField()
    definition = models.TextField()


class DuolingoUsers(models.Model):
    username = models.CharField(max_length=100, unique=True)
    last_update = models.DateField(blank=True, null=True)
    last_inquiry = models.DateField(auto_now=True)

