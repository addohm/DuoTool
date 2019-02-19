# import requests
import random
from modules.duolingo import Duolingo
from django.shortcuts import render, redirect, HttpResponseRedirect
from decouple import config
from pprint import pprint

from main.models import HanDictionary
from .forms import TestForm, HskLevelSelectForm


def get_hsk_phrases(level):
    model = HanDictionary
    phrasedict = {}
    i = 0
    phraselist = model.objects.filter(hsk_level__lte=level).filter(hsk_level__gt=0).order_by('?')[:5]
    for item in phraselist:
        phrasedict[phraselist[i].simplified] = {
            'id': phraselist[i].pk,
            'pinyin': phraselist[i].pinyin,
            'definition': phraselist[i].definition.replace(';', ',').replace('  ', ' ')[:-1],
        }
        i += 1
    # pprint(phrasedict)
    # word: {'id': phraseid, 'pinyin': pinyin,  'definition': definition}
    return phrasedict


def get_test_words(words):
    wordlist = []
    while len(wordlist) < 5:
        word = random.choice(words)
        if word not in wordlist:
            wordlist.append(word)
    return wordlist


def get_word_dict(phraselist):
    model = HanDictionary
    phrasedict = {}
    for phrase in phraselist:
        results = model.objects.filter(simplified__iexact=phrase)
        for i in range(len(results)):
            # use the last id key found
            phraseid = results[i].pk
            if i == 0:
                definition = results[i].definition.replace(';', ' ')
            else:
                definition = definition + '; ' + results[i].definition
            definition = definition.replace(';', ',').replace('  ', ' ')[:-1]
            pinyin = results[i].pinyin
        phrasedict[phrase] = {
            'id': phraseid,
            'pinyin': pinyin,
            'definition': definition
        }
    # pprint(phrasedict)
    # word: {'id': phraseid, 'pinyin': pinyin,  'definition': definition}
    return phrasedict


def duolingo_test(request, username='addohm', password=None):
    lingo = Duolingo(config('USER'), config('PASS'))
    streakinfo = lingo.get_streak_info()
    context = {
        'username': username,
        'streakinfo': streakinfo,
    }
    template_name = 'tests/test.html'
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the saved answer dictionary:
        print('POSTING TEST RESULTS')
        form = TestForm(data=request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            print('PASSED')
            # redirect to a new URL:
            return redirect('main:success')
        else:  
            print('FAILED')
            if form.has_error:
                print('FORM ERROR')
            pass
    # if a GET (or any other method) we'll create a blank form
    else:
        print('GETTING NEW TEST')
        phrases = lingo.get_known_phrases()
        testwords = get_test_words(phrases)
        wordsdict = get_word_dict(testwords)
        form = TestForm(wordsdict)
    context['form'] = form
    return render(request, template_name, context)


def hsk_test(request, level, username=None):
    template_name = 'tests/test.html'
    context = {
        'username': username,
    }
    if request.method == 'POST':
        # create a form instance and populate it with data from the saved answer dictionary:
        print('POSTING TEST RESULTS')
        form = TestForm(data=request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            print('PASSED')
            # redirect to a new URL:
            return redirect('main:success')
        else:  
            print('FAILED')
            if form.has_error:
                print('FORM ERROR')
            pass
    # if a GET (or any other method) we'll create a blank form
    else:
        print('GETTING NEW TEST')
        wordsdict = get_hsk_phrases(level)
        form = TestForm(wordsdict)
    context['form'] = form
    return render(request, template_name, context)


def hsk_select(request, username=None):
    template_name = 'tests/hsklevelselect.html'
    if request.method == 'POST':
        form = HskLevelSelectForm(request.POST)
        if form.is_valid():
            level = form.cleaned_data['level']
            return redirect('tests:hsktest', level=level)
    else:
        form = HskLevelSelectForm()
    context = {
        'form': form,
        'username': username,
    }
    return render(request, template_name, context)
    