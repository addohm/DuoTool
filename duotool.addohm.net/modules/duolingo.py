import json
import os
import random
import re
import sys
import requests
import bs4
from decouple import Csv, config

__version__ = "0.0"
__forkauthor__ = "Adam S. Leven"
__email__ = "addohm@users.noreply.github.com"
__url__ = "https://github.com/addohm/Duolingo"

_resource_path = os.path.join('/' + '/'.join(os.path.dirname(sys.argv[0]).split('/')[1:-1]), 'static/json')

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class AlreadyHaveStoreItemException(Exception):
    pass


class Duolingo(object):
    def __init__(self, username, password=None):
        self.username = username
        self.password = password
        self.user_url = "https://www.duolingo.com/users/%s" % self.username
        self.vocab_url = 'https://www.duolingo.com/vocabulary/overview'
        self.session = requests.Session()
        self.leader_data = None
        self.jwt = None
        self._resource_path = os.path.join('/' + '/'.join(os.path.dirname(sys.argv[0]).split('/')[1:-1]), 'static/json')


        # use below if testing with runserver
        if not __name__ == '__main__':
            # Assume module imported by django
            from django.conf import settings
            self._resource_path = os.path.join(settings.BASE_DIR, 'static/json')
            if password:
                self._login()

            self.user_data = self.request_userdata()
            self.user_vocab = self.request_uservocab()
        else:
        # Update global _resource_path variable
            _resource_path = self._resource_path

            self._user_path = os.path.join(self._resource_path, 'userdata.json')
            self._vocab_path = os.path.join(self._resource_path, 'uservocab.json')
            with open(self._user_path, encoding='utf-8') as user_data:
                self.user_data = json.load(user_data)
                user_data.close()
            with open(self._vocab_path, encoding='utf-8') as vocab_data:
                self.user_vocab = json.load(vocab_data)
                vocab_data.close()


    def _login(self):
        """
        Authenticate through ``https://www.duolingo.com/login``.
        """
        login_url = "https://www.duolingo.com/login"
        data = {"login": self.username, "password": self.password}
        request = self._make_req(login_url, data)
        attempt = request.json()

        if attempt.get('response') == 'OK':
            self.jwt = request.headers['jwt']
            return True

        raise Exception("Login failed")

    def _make_req(self, url, data=None):
        headers = {}
        if self.jwt is not None:
            headers['Authorization'] = 'Bearer ' + self.jwt
        req = requests.Request('POST' if data else 'GET',
                               url,
                               json=data,
                               headers=headers,
                               cookies=self.session.cookies)
        prepped = req.prepare()
        return self.session.send(prepped)

    def get_settings(self):
        """Get user settings."""
        keys = ['notify_comment', 'deactivated', 'is_follower_by',
                'is_following']

        return self._make_dict(keys, self.user_data)

    def request_userdata(self):
        """
        Get user's data from ``https://www.duolingo.com/users/<username>. - WORKS
        """
        u = self._make_req(self.user_url)
        return u.json()

    def request_uservocab(self):
        """
        Get user's vocab from ``https://www.duolingo.com/vocabulary/overview``. - WORKS
        """
        v = self._make_req(self.vocab_url)
        return v.json()

    def get_activity_stream(self, before=None):
        """
        Get user's activity stream from
        ``https://www.duolingo.com/stream/<user_id>?before=<date> if before - BROKEN
        date is given or else
        ``https://www.duolingo.com/activity/<user_id>``  - BROKEN

        :param before: Datetime in format '2015-07-06 05:42:24'
        :type before: str
        :rtype: dict
        """
        # if before:
        #     url = "https://www.duolingo.com/stream/{}?before={}"
        #     url = url.format(self.user_data.id, before)
        # else:
        #     url = "https://www.duolingo.com/activity/{}"
        #     url = url.format(self.user_data.id)
        # request = self._make_req(url)
        # try:
        #     return request.json()
        # except:
        #     raise Exception('Could not get activity stream')
        pass

    def get_leaderboard(self, unit=None, before=None):
        """
        Get user's rank in the week in descending order, stream from

        ``https://www.duolingo.com/friendships/leaderboard_activity?unit=week&_=time`` - WORKS

        :param before: Datetime in format '2015-07-06 05:42:24'
        :param unit: maybe week or month
        :type before: str
        :type unit: str
        :rtype: List
        """
        if unit:
            url = 'https://www.duolingo.com/friendships/leaderboard_activity?unit={}&_={}'
        else:
            raise Exception('Needs unit as argument (week or month)')

        if before:
            url = url.format(unit, before)
        else:
            raise Exception('Needs str in Datetime format "%Y.%m.%d %H:%M:%S"')

        self.leader_data = self._make_req(url).json()
        data = []
        for result in iter(self.get_friends()):
            for value in iter(self.leader_data['ranking']):
                if result['id'] == int(value):
                    temp = {'points': int(self.leader_data['ranking'][value]),
                            'unit': unit,
                            'id': result['id'],
                            'username': result['username']}
                    data.append(temp)

        return sorted(data, key=lambda user: user['points'], reverse=True)
        pass

    def buy_item(self, item_name, abbr):
        url = 'https://www.duolingo.com/2017-06-30/users/{}/purchase-store-item'
        url = url.format(self.user_data.id)

        data = {'name': item_name, 'learningLanguage': abbr}
        request = self._make_req(url, data)

        """
        status code '200' indicates that the item was purchased
        returns a text like: {"streak_freeze":"2017-01-10 02:39:59.594327"}
        """

        if request.status_code == 400 and request.json()['error'] == 'ALREADY_HAVE_STORE_ITEM':
            raise AlreadyHaveStoreItemException(
                'Already equipped with ' + item_name + '.')
        if not request.ok:
            # any other error:
            raise Exception('Not possible to buy item.')

    def buy_streak_freeze(self):
        """
        figure out the users current learning language
        use this one as parameter for the shop
        """
        lang = self.get_abbreviation_of(
            self.get_user_info()['learning_language_string'])
        if lang is None:
            raise Exception('No learning language found')
        try:
            self.buy_item('streak_freeze', lang)
            return True
        except Exception as e:
            if e.args[0] == 'Already equipped with streak freeze.':
                # we are good
                return False
            else:
                # unknown exception, raise it again
                raise Exception(e.args)
        except AlreadyHaveyStoreItemException:
            return False

    def _switch_language(self, lang):
        """
        Change the learned language with
        ``https://www.duolingo.com/switch_language``.

        :param lang: Wanted language abbreviation (example: ``'fr'``)
        :type lang: str
        """
        data = {"learning_language": lang}
        url = "https://www.duolingo.com/switch_language"
        request = self._make_req(url, data)

        try:
            parse = request.json()['tracking_properties']
            if parse['learning_language'] == lang:
                self.user_data = Struct(**self._get_data())
        except:
            raise Exception('Failed to switch language')

    @staticmethod
    def _make_dict(keys, array):
        data = {}

        for key in keys:
            if type(array) == dict:
                data[key] = array[key]
            else:
                data[key] = getattr(array, key, None)

        return data

    @staticmethod
    def _compute_dependency_order(skills):
        """
        Add a field to each skill indicating the order it was learned
        based on the skill's dependencies. Multiple skills will have the same
        position if they have the same dependencies.
        """
        # # Key skills by first dependency. Dependency sets can be uniquely
        # # identified by one dependency in the set.
        # dependency_to_skill = MultiDict([(skill['dependencies_name'][0]
        #                                   if skill['dependencies_name']
        #                                   else '',
        #                                   skill)
        #                                  for skill in skills])
        # # Start with the first skill and trace the dependency graph through
        # # skill, setting the order it was learned in.
        # index = 0
        # previous_skill = ''
        # while True:
        #     for skill in dependency_to_skill.getlist(previous_skill):
        #         skill['dependency_order'] = index
        #     index += 1
        #     # Figure out the canonical dependency for the next set of skills.
        #     skill_names = set([skill['name']
        #                        for skill in
        #                        dependency_to_skill.getlist(previous_skill)])
        #     canonical_dependency = skill_names.intersection(
        #         set(dependency_to_skill.keys()))
        #     if canonical_dependency:
        #         previous_skill = canonical_dependency.pop()
        #     else:
        #         # Nothing depends on these skills, so we're done.
        #         break
        # return skills
        pass

    def get_languages(self, abbreviations=False):
        """
        Get praticed languages.

        :param abbreviations: Get language as abbreviation or not
        :type abbreviations: bool
        :return: List of languages
        :rtype: list of str
        """
        data = []

        for lang in self.user_data['languages']:
            if lang['learning']:
                if abbreviations:
                    data.append(lang['language'])
                else:
                    data.append(lang['language_string'])

        return data

    def get_language_from_abbr(self, abbr):
        """Get language full name from abbreviation."""
        for language in self.user_data['languages']:
            if language['language'] == abbr:
                return language['language_string']
        return None

    def get_abbreviation_of(self, name):
        """Get abbreviation of a language."""
        for language in self.user_data['languages']:
            if language['language_string'] == name:
                return language['language']
        return None

    def get_language_details(self, language):
        """Get user's status about a language."""
        for lang in self.user_data['languages']:
            if language == lang['language_string']:
                return lang
        return {}

    def get_user_info(self):
        """Get user's informations."""
        # 'num_following', 'num_followers' moved to the tracking_properties dict
        # havent found contribution_points or invites left
        # social media ids causing trouble when making the dict 'gplus_id', 'twitter_id',
        # All of which have been removed.
        fields = ['username', 'bio', 'id', 'cohort',
                  'language_data', 'learning_language_string',
                  'created', 'admin', 'location', 'fullname',
                  'avatar', 'ui_language']

        return self._make_dict(fields, self.user_data)

    def get_certificates(self):
        """Get user's certificates."""
        for certificate in self.user_data.certificates:
            certificate['datetime'] = certificate['datetime'].strip()

        return self.user_data.certificates

    def get_streak_info(self):
        """
        Get user's streak informations.
        :returns: dict ``{'daily_goal': int, 'site_streak': int, 'streak_extended_today': bool}``
        """
        fields = ['daily_goal', 'site_streak', 'streak_extended_today']
        return self._make_dict(fields, self.user_data)

    def _is_current_language(self, abbr):
        """Get if user is learning a language."""
        return abbr in self.user_data['language_data'].keys()

    def get_calendar(self, language_abbr=None):
        """Get user's last actions."""
        if language_abbr:
            if not self._is_current_language(language_abbr):
                self._switch_language(language_abbr)
            return self.user_data['language_data'][language_abbr]['calendar']
        else:
            return self.user_data['calendar']

    def get_language_progress(self, lang):
        """Get informations about user's progression in a language."""
        if not self._is_current_language(lang):
            self._switch_language(lang)

        fields = ['streak', 'language_string', 'level_progress',
                  'num_skills_learned', 'level_percent', 'level_points',
                  'points_rank', 'next_level', 'level_left', 'language',
                  'points', 'fluency_score', 'level']

        return self._make_dict(fields, self.user_data['language_data'][lang])

    def get_friends(self):
        """Get user's friends."""
        for k, v in iter(self.user_data['language_data'].items()):
            data = []
            for friend in v['points_ranking_data']:
                temp = {'username': friend['username'],
                        'id': friend['id'],
                        'points': friend['points_data']['total'],
                        'languages': [i['language_string'] for i in
                                      friend['points_data']['languages']]}
                data.append(temp)

            return data

    def get_known_words(self, lang):
        """Get a list of all words learned by user in a language."""
        words = []
        for topic in self.user_data['language_data'][lang]['skills']:
            if topic['learned']:
                words += topic['words']
        return set(words)

    def get_learned_skills(self, lang):
        """
        Return the learned skill objects sorted by the order they were learned
        in.
        """
        skills = [skill for skill in
                  self.user_data.language_data[lang]['skills']]
        self._compute_dependency_order(skills)
        return [skill for skill in
                sorted(skills, key=lambda skill: skill['dependency_order'])
                if skill['learned']]

    def get_known_topics(self, lang):
        """Return the topics learned by a user in a language."""
        return [topic['title']
                for topic in self.user_data['language_data'][lang]['skills']
                if topic['learned']]

    def get_unknown_topics(self, lang):
        """Return the topics remaining to learn by a user in a language."""
        return [topic['title']
                for topic in self.user_data['language_data'][lang]['skills']
                if not topic['learned']]

    def get_golden_topics(self, lang):
        """Return the topics mastered ("golden") by a user in a language."""
        return [topic['title']
                for topic in self.user_data['language_data'][lang]['skills']
                if topic['learned'] and topic['strength'] == 1.0]

    def get_reviewable_topics(self, lang):
        """Return the topics learned but not golden by a user in a language."""
        return [topic['title']
                for topic in self.user_data.language_data[lang]['skills']
                if topic['learned'] and topic['strength'] < 1.0]

    def get_translations(self, words, source=None, target=None):
        """
        Get words' translations from
        ``https://d2.duolingo.com/api/1/dictionary/hints/<source>/<target>?tokens=``<words>``

        :param words: A single word or a list
        :type: str or list of str
        :param source: Source language as abbreviation
        :type source: str
        :param target: Destination language as abbreviation
        :type target: str
        :return: Dict with words as keys and translations as values
        """
        if not source:
            source = self.user_data.ui_language
        if not target:
            target = list(self.user_data.language_data.keys())[0]

        word_parameter = json.dumps(words, separators=(',', ':'))
        url = "https://d2.duolingo.com/api/1/dictionary/hints/{}/{}?tokens={}" \
            .format(target, source, word_parameter)

        request = self.session.get(url)
        try:
            return request.json()
        except:
            raise Exception('Could not get translations')

    def get_vocabulary(self, language_abbr=None):
        """Get overview of user's vocabulary in a language."""
        if not self.password:
            raise Exception("You must provide a password for this function")
        if language_abbr and not self._is_current_language(language_abbr):
            self._switch_language(language_abbr)

        overview_url = "https://www.duolingo.com/vocabulary/overview"
        overview_request = self._make_req(overview_url)
        overview = overview_request.json()

        return overview

    _cloudfront_server_url = None
    _homepage_text = None

    @property
    def _homepage(self):
        if self._homepage_text:
            return self._homepage_text
        homepage_url = "https://www.duolingo.com"
        request = self._make_req(homepage_url)
        self._homepage_text = request.text
        return self._homepage

    @property
    def _cloudfront_server(self):
        if self._cloudfront_server_url:
            return self._cloudfront_server_url

        server_list = re.search('//.+\.cloudfront\.net', self._homepage)
        self._cloudfront_server_url = "https:{}".format(server_list.group(0))

        return self._cloudfront_server_url

    _tts_voices = None

    # def _process_tts_voices(self):
    #     voices_js = re.search('duo\.tts_multi_voices = {.+};',
    #                           self._homepage).group(0)
    #     voices = voices_js[voices_js.find("{"):voices_js.find("}") + 1]
    #     self._tts_voices = json.loads(voices)

    # def _get_voice(self, language_abbr, rand=False, voice=None):
    #     if not self._tts_voices:
    #         self._process_tts_voices()
    #     if voice and voice != 'default':
    #         return '{}/{}'.format(language_abbr, voice)
    #     if rand:
    #         return random.choice(self._tts_voices[language_abbr])
    #     else:
    #         return self._tts_voices[language_abbr][0]

    # def get_language_voices(self, language_abbr=None):
    #     if not language_abbr:
    #         language_abbr = list(self.user_data.language_data.keys())[0]
    #     voices = []
    #     if not self._tts_voices:
    #         self._process_tts_voices()
    #     for voice in self._tts_voices[language_abbr]:
    #         if voice == language_abbr:
    #             voices.append('default')
    #         else:
    #             voices.append(voice.replace('{}/'.format(language_abbr), ''))
    #     return voices

    # def get_audio_url(self, word, language_abbr=None, random=True, voice=None):
    #     if not language_abbr:
    #         language_abbr = list(self.user_data.language_data.keys())[0]
    #     tts_voice = self._get_voice(language_abbr, rand=random, voice=voice)
    #     return "{}/tts/{}/token/{}".format(self._cloudfront_server, tts_voice,
    #                                        word)

    # def get_related_words(self, word, language_abbr=None):
    #     if not self.password:
    #         raise Exception("You must provide a password for this function")
    #     if language_abbr and not self._is_current_language(language_abbr):
    #         self._switch_language(language_abbr)

    #     overview_url = "https://www.duolingo.com/vocabulary/overview"
    #     overview_request = self._make_req(overview_url)
    #     overview = overview_request.json()

    #     for word_data in overview['vocab_overview']:
    #         if word_data['normalized_string'] == word:
    #             related_lexemes = word_data['related_lexemes']
    #             return [w for w in overview['vocab_overview']
    #                     if w['lexeme_id'] in related_lexemes]

    def get_all_languages(self):
        """
        Gets all of the languages being worked on by the user
        """
        languages  = {}
        abbr, txt = [], []
        for lang in self.user_data['languages']:
            if lang['learning']:
                abbr.append(lang['language'])
                txt.append(lang['language_string'])
                languages = dict(zip(abbr, txt))
        return languages

    def get_current_language(self):
        """
        Gets the currently selected language
        """
        return self.user_data['learning_language']

    def _get_explanations(self, language=None):
        """
        Gets the full set of lesson explanations as a dict
        """
        if language is None:
            language = self.get_current_language()
        explanation = {}
        for i in range(len(self.user_data['language_data'][language]['skills'])):
            e = self.user_data['language_data'][language]['skills'][i]['explanation']
            if e is not None:
                explanation[i] = e
        return explanation

    def _check_vocab(self, word):
        """
        Checks the word supplied against the current vocab

        :param word: a word
        :type word: str
        """
        words = []
        for i in self.user_vocab['vocab_overview']:
            words.append(i.get("word_string"))
        if word in words:
            return True
        else:
            return False

    def get_word_audio_url(self, word):
        """
        Returns the url to play word associated audio

        :param word: a word
        :type word: str
        """
        if word is None:
            raise Exception('A word must be specified to use this function')
        if not self._check_vocab(word):
            raise Exception('The word specified does not exist in your current vocabulary')
        baseurl = self.get_voice_url()
        return baseurl + str(word)

    def _get_link_references(self, explanations):
        """
        Gets a list of links from the lesson explanations
        """
        voice = ''
        for i in explanations:
            voice = self._find_link(explanations[i])
            if len(voice) > 0:
                return voice
        return None
        
    def _find_link(self, explanation):
        """
        Identifys and returns the full link from the html
        """
        soup = bs4.BeautifulSoup(explanation, 'lxml')
        links = soup.find_all('a')
        return links

    def get_voice_url(self):
        """
        Gets the first voice name that occurs within the array of
        explanations of the currently selected language

        :param language: language in it's abbreviated format
        :param explanation: explanation array for lessons
        :type language: dict
        :type explanation: dict
        """
        language = self.get_current_language()

        explanation = self._get_explanations(language)

        # Get the full url from an explanation
        fullurl = self._get_link_references(explanation)

        # Clean up the full url to get the game
        name = str(fullurl[0]).split('/')[3]

        # Get the url base
        urlbase = self.user_data.get('tts_base_url', None)

        # Get the language as a string
        # language = next(iter(language))

        # Format the url
        url = urlbase + 'tts/' + language + '/' + name + '/token/'

        return url

    def get_lesson_info(self):
        """
        Weave the word lists for the currently selected language in with the lesson explanation
        :return: The full dict of lesson word sets with associated id and explanation
        :rtype: dict of ``{wordlist: {'id', 'explanation'}}``
        """
        wordlistdict = {}
        userdata = self.get_user_info()
        lang = self.get_current_language()
        for item in userdata['language_data'][lang]['skills']:
            if item.get('levels_finished') > 0:
                lessonwords = item.get("words")
                explanation = item.get("explanation")
                lessonname = item.get("Title")
                wordlistdict_id = item.get("id")
                wordlistdict[str(lessonwords)] = {'id': wordlistdict_id, 'name': lessonname, 'explanation': explanation}
        return wordlistdict

    def get_unique_words(self):
        """
        Get list of unique words of the currently selected language
        :return: set of words
        :rtype: set of str
        """
        # Get current language
        nowlang = self.get_current_language()
        # Get sorted list from the current language
        words = self.get_known_words(nowlang)
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

    
############################## Django views.py test functions #############################

def get_hanzi_dict():
    json_path = os.path.join(_resource_path, 'hanzidb.json')
    with open(json_path, encoding='utf-8') as json_data:
        hanzidict = json.load(json_data)
    json_data.close()
    return hanzidict


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
                words[word]['lesson_id'] = lessoninfo[lesson]['id']
    return words

def get_test_words(words):
    wordlist = []
    while len(wordlist) <= 20:
        word = random.choice(words)
        if word not in wordlist:
            wordlist.append(word)
    return wordlist
############################## End Django views.py test functions #############################

attrs = [
    'settings', 'languages', 'user_info', 'certificates', 'streak_info',
    'calendar', 'language_progress', 'friends', 'known_words',
    'learned_skills', 'known_topics', 'activity_stream', 'vocabulary',
    'all_languages', 'current_language', 'word_audio_url',
    'voice_url', 'lesson_info', 'unique_words', 
]

for attr in attrs:
    getter = getattr(Duolingo, "get_" + attr)
    prop = property(getter)
    setattr(Duolingo, attr, prop)


if __name__ == '__main__':
    from pprint import pprint

    lingo = Duolingo(config('USER'), config('PASS'))
    
    # duolingo = Duolingo('Thomas.Heiss')
    # u = duolingo.request_userdata()
    # v = duolingo.request_uservocab()
    # ui = lingo.get_user_info()
    # st = lingo.get_streak_info()
    # p = lingo.get_language_progress('zs')
    # lb = duolingo.get_leaderboard('week', 'time')
    # knowntopic = duolingo.get_known_topics('zs')
    # ll = duolingo.get_languages(abbreviations=True)
    # c = duolingo.get_calendar()
    # w = duolingo.get_known_words('zs')
    # s = duolingo.get_learned_skills('zs') # BROKEN
    # t = duolingo.get_known_topics('zs')
    # tr = duolingo.get_translations('儿子', 'en', 'zs')
    # v = duolingo.get_vocabulary('zs')
    # lv = duolingo.get_language_voices() # BROKEN at _process_tts_voices
    # au = duolingo.get_audio_url('你') # BROKEN at _process_tts_voices
    # rw = duolingo.get_related_words('你') # ?Returns none?
    word_list = lingo.get_unique_words()
    # word_dict = make_word_dict(word_list)
    # lessoninfo = lingo.get_lesson_info()
    # wordsdict = associate_words_lessons(word_dict, lessoninfo)
    # wordsdict = associate_words_lessons(make_word_dict(get_unique_words(lingo)), make_lession_info(lingo))
    # lessoninfo = make_lession_info(lingo)
    testwords = get_test_words(word_list)
    pprint(testwords)