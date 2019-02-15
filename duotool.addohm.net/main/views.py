import requests
import os
import json
from django.conf import settings
from django.shortcuts import render


def getUserData(url):
    i = 0
    char, wordlists = {}, {}
    response = requests.get(url)
    userdata = response.json()
    # Import json for character statistics
    json_path = os.path.join(settings.BASE_DIR, 'static/json/hanzidb.json')
    # json_path = 'DuoTool/duotool.addohm.net/static/json/hanzidb.json'
    with open(json_path, encoding='utf-8') as json_data:
        word_data = json.load(json_data)
        for lang in userdata['language_data']:
            for item in userdata['language_data'][lang]['skills']:
                i += 1
                if item.get('levels_finished') > 0:
                    explanation = {}
                    explanation['index'] = i
                    lessonwords = item.get("words")
                    wordlists[str(lessonwords)] = []
                    explanation['explanation'] = item.get("explanation")
                    wordlists[str(lessonwords)].append(explanation)
                    for word in lessonwords:
                        wordinfo = {}
                        wordinfo['index'] = i
                        if word in word_data:
                            wordinfo['pinyin'] = word_data[word][0]['pinyin']
                            wordinfo['definition'] = word_data[word][0]['definition']
                        else:
                            wordinfo['pinyin'] = ''
                            wordinfo['definition'] = ''
                        char[word] = []
                        char[word].append(wordinfo)
    return char, wordlists


def home(request, username='addohm'):
    template_name = 'main/index.html'

    if request.method == 'POST':
        username = request.POST['username']

    url = "https://www.duolingo.com/users/{}".format(username)
    char, wordlists = getUserData(url)  # catch value of dictionary
    context = {
        'username': username,
        'char': char,
        'wordlists': wordlists,
    }
    return render(request, template_name, context)

