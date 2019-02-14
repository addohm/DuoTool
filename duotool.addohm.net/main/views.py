# import requests
import os
import json
from modules.duolingo import Duolingo
from django.conf import settings
from django.shortcuts import render
from decouple import config, Csv
from pprint import pprint


def get_hanzi_dict():
    # json_path = 'DuoTool/duotool.addohm.net/static/json/hanzidb.json'
    json_path = os.path.join(settings.BASE_DIR, 'static/json/hanzidb.json')
    with open(json_path, encoding='utf-8') as json_data:
        hanzidict = json.load(json_data)
    json_data.close()
    return hanzidict

def get_unique_words(lingo):
    # Get current language
    nowlang = lingo.get_current_language()
    # Get sorted list from the current language
    words = lingo.get_known_words(nowlang)
    wordlist = []
    for item in words:
        # if it's a single character, store it
        if len(item) == 1:
            wordlist.insert(len(wordlist), item)
        # if it's multiple characters, split them then store it
        if len(item) > 1:
            for char in item:
                wordlist.insert(len(wordlist), char)
    # return as a sorted list of unique characters
    return sorted(set(wordlist), key=len)


def make_word_dict(wordlist, hanzidict=None):
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
        else:
            pinyin = ''
            definition = ''
        word_id += 1
        worddict[word] = {'id': word_id, 'lesson_id': 0, 'pinyin': pinyin, 'definition': definition}
    return worddict

def make_lession_info(lingo):
    """
    Weave the word lists for the currently selected language in with the lesson explanation
    :lingo dict: The full list of known words cleaned up
    ``{wordlist: {'id', 'explanation'}}``
    """
    wordlistdict = {}
    wordlistdict_id = 0
    userdata = lingo.get_user_info()
    lang = lingo.get_current_language()
    for item in userdata['language_data'][lang]['skills']:
        if item.get('levels_finished') > 0:
            lessonwords = item.get("words")
            explanation = item.get("explanation")
            wordlistdict_id += 1
            wordlistdict[str(lessonwords)] = {'id': wordlistdict_id, 'explanation': explanation}
    return wordlistdict

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
                words[word]['lesson_id'] = lessoninfo[lesson]['id']
    return words

def getUserData(lingo):
    """
    get all the words as individual items and attach it's pinyin and definition
    and
    get all the lession word groups and
    """
    word_list = get_unique_words(lingo)
    word_dict = make_word_dict(word_list)
    lessoninfo = make_lession_info(lingo)
    wordsdict = associate_words_lessons(word_dict, lessoninfo)

    # with open(os.path.join(settings.BASE_DIR, 'static/json/char.json'), 'w') as f:
    #     json.dump(char, f, indent=2, ensure_ascii=False)
    # with open(os.path.join(settings.BASE_DIR, 'static/json/wordlists.json'), 'w') as f:
    #     json.dump(wordlists, f, indent=2, ensure_ascii=False)
    return wordsdict, lessoninfo


"""
{
  "要": [
    {
      "index": 5,
      "pinyin": "yào",
      "definition": "necessary, essential; necessity"
    }
  ],
  ...
  ...
}
------------------------------------------------------------------------------------
{
  "['要', '热', '冰', '牛奶', '咖啡', '牛', '奶', '咖', '啡']": [
    {
      "index": 5,
      "explanation": "<h4><strong>Want</strong></h4>\n<p>The verb 要 yào has many uses. One function is to indicate \"wanting something\". You should follow the pattern \"subject + 要 + object\". To negate this wanting, you can simply place 不 before 要.</p>\n<p>You can also use 要 to express \"wanting to do something\" via the pattern \"subject + 要 + verb\".</p>\n<table>\n<thead>\n<tr>\n<th>Chinese</th>\n<th>Pinyin</th>\n<th>English</th>\n</tr>\n</thead>\n<tbody>\n<tr>\n<td>我要你的电话号码。</td>\n<td>Wǒ yào nǐ de diànhuà hàomǎ.</td>\n<td>I want your phone number.</td>\n</tr>\n<tr>\n<td>我不要他的电话号码。</td>\n<td>Wǒ bǔ[bú] yào tā de diànhuà hàomǎ.</td>\n<td>I don't want his phone number.</td>\n</tr>\n<tr>\n<td>学生们要喝水。</td>\n<td>Xuéshēng men yào hē shuǐ.</td>\n<td>Students want to drink water.</td>\n</tr>\n<tr>\n<td>老师们不要喝茶。</td>\n<td>Lǎoshī men bù[bú] yào hē chá.</td>\n<td>Teachers don’t want to drink tea.</td>\n</tr>\n</tbody>\n</table>"
    }
  ],
  ...
  ...
}
"""


def home(request, username='addohm', password=None):
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
    wordslist, lessoninfo = getUserData(lingo)  # catch value of dictionary
    context = {
        'username': username,
        'char': wordslist,
        'wordlists': lessoninfo,
    }
    return render(request, template_name, context)

