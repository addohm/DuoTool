from rest_framework import serializers
from .models import HanDictionary as dictionary


class PhrasesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = dictionary
        fields = ('traditional', 'simplified', 'pinyin', 'simplified_radical',
        'hsk_level', 'frequency_rank', 'phrase_url', 'radical_url', 'definition')
