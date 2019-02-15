# import requests
import os
import json
import random
from modules.duolingo import Duolingo
from django.conf import settings
from django.shortcuts import render, redirect, HttpResponseRedirect
from decouple import config, Csv
from pprint import pprint

from .forms import TestForm

def get_hanzi_dict():
    # json_path = 'DuoTool/duotool.addohm.net/static/json/hanzidb.json'
    json_path = os.path.join(settings.BASE_DIR, 'static/json/hanzidb.json')
    with open(json_path, encoding='utf-8') as json_data:
        hanzidict = json.load(json_data)
    json_data.close()
    return hanzidict

def get_word_dict(wordlist, hanzidict=None):
    """
    Weave the known words in with the dictionary pronounciation and definition
    :wordlist set: The full list of known words cleaned up
    :hanzidict dict: The full hanzi dictionary
    ``{word: {'id', 'lesson_id', 'pinyin', 'definition'}}``
    """
    if hanzidict is None:
        hanzidict = get_hanzi_dict()
    worddict = {}
    word_id = 0
    for word in wordlist:
        if word in hanzidict:
            pinyin = hanzidict[word][0]['pinyin']
            definition = hanzidict[word][0]['definition']
            hsklevel = int(hanzidict[word][0]['hsk_level'])
            frequency = round(((int(hanzidict[word][0]['frequency_rank']) / 10000) - 1) * -100, 1)
        else:
            pinyin = ''
            definition = ''
        word_id += 1
        worddict[word] = {'id': word_id, 'lesson_id': 0, 'pinyin': pinyin,
            'definition': definition, 'hsklevel': hsklevel, 'frequency': frequency}
    return worddict

def associate_words_lessons(words, lessoninfo):
    """
    Update the word dictioary with the appropriate lesson ids
    """
    if words is None:
        raise Exception("Supplied word list contains nothing")
    if lessoninfo is None:
        raise Exception("Supplied lesson info contains nothing")
    for word in words:
        for lesson in lessoninfo:
            if word in lesson:
                words[word].update({'lesson_id': lessoninfo[lesson]['id']})
    return words


def get_test_words(words):
    wordlist = []
    while len(wordlist) <= 20:
        word = random.choice(words)
        if word not in wordlist:
            wordlist.append(word)
    return wordlist

def home(request, username=None):
    # import pdb
    # pdb.set_trace()
    template_name = 'main/index.html'

    if request.method == 'POST':
        username = request.POST['username']

    lingo = Duolingo(config('USER'), config('PASS'))
    # with open(os.path.join(settings.BASE_DIR, 'static/json/userdata.json'), 'w') as f:
    #     json.dump(lingo.user_data, f, indent=2, ensure_ascii=False)
    # with open(os.path.join(settings.BASE_DIR, 'static/json/vocab.json'), 'w') as f:
    #     json.dump(lingo.user_vocab, f, indent=2, ensure_ascii=False)
    word_list = lingo.get_unique_words()
    word_dict = get_word_dict(word_list)
    lessoninfo = lingo.get_lesson_info()
    wordsdict = associate_words_lessons(word_dict, lessoninfo)
    voiceurl = lingo.get_voice_url()
    streakinfo = lingo.get_streak_info()
    context = {
        'username': username,
        'char': wordsdict,
        'wordlists': lessoninfo,
        'voiceurl': voiceurl,
        'streakinfo': streakinfo,
    }
    return render(request, template_name, context)

def test(request, username='addohm'):
    template_name = 'main/test.html'

    if request.method == 'POST':
        username = request.POST['username']

    lingo = Duolingo(config('USER'), config('PASS'))
    streakinfo = lingo.get_streak_info()
    uniquewords = lingo.get_unique_words()
    testwords = get_test_words(uniquewords)
    wordsdict = get_word_dict(testwords)
    context = {
        'username': username,
        'streakinfo': streakinfo,
        'testwords': testwords,
        'wordsdict': wordsdict,
    }
    return render(request, template_name, context)

def get_test(request, username='addohm'):
    template_name = 'main/test.html'
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = TestForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        lingo = Duolingo(config('USER'), config('PASS'))
        streakinfo = lingo.get_streak_info()
        uniquewords = lingo.get_unique_words()
        testwords = get_test_words(uniquewords)
        wordsdict = get_word_dict(testwords)
        form = TestForm(wordsdict)
        context = {
            'username': username,
            'streakinfo': streakinfo,
            'wordsdict': wordsdict,
            'form': form,
        }

    return render(request, template_name, context)