import json
import requests
import re
import sys
import os
import random
import bs4
from decouple import Csv, config


__version__ = "0.1"
__originalauthor__ = "Adam S. Leven"
__email__ = "addohm@hotmail.com"
__url__ = "https://github.com/addohm/Duolingo"

    
class Duolingo(object):
    def __init__(self, username, password=None):
        self._resource_path = os.path.join(os.path.dirname(sys.argv[0]), 'resources')
        self._dictionary_path = os.path.join(self._resource_path, 'hanzidb.json')
        self._user_path = os.path.join(self._resource_path, 'userdata.json')
        self._vocab_path = os.path.join(self._resource_path, 'uservocab.json')

        with open(self._dictionary_path, encoding='utf-8') as dictionary_data:
            self.dictionary_data = json.load(dictionary_data)
            dictionary_data.close()
        with open(self._user_path, encoding='utf-8') as user_data:
            self.user_data = json.load(user_data)
            user_data.close()
        with open(self._vocab_path, encoding='utf-8') as vocab_data:
            self.user_vocab = json.load(vocab_data)
            vocab_data.close()

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

    def get_explanations(self, lang):
        """
        Gets the full set of lesson explanations as a dict
        """
        languages = self.get_current_language()
        explanation = {}
        for lang in languages:
            for i in range(len(self.user_data['language_data'][lang]['skills'])):
                e = self.user_data['language_data'][lang]['skills'][i]['explanation']
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
        Gets the first voice name that occurs within the array of explanations

        :param language: language in it's abbreviated format
        :param explanation: explanation array for lessons
        :type language: dict
        :type explanation: dict
        """
        language = self.get_current_language()

        explanation = self.get_explanations(language)

        # Get the full url from an explanation
        fullurl = self._get_link_references(explanation)

        # Clean up the full url to get the game
        name = str(fullurl[0]).split('/')[3]

        # Get the url base
        urlbase = self.user_data.get('tts_base_url', None)

        # Get the language as a string
        language = next(iter(language))

        # Format the url
        url = urlbase + 'tts/' + language + '/' + name + '/'

        return url

if __name__ == '__main__':
    from pprint import pprint

    duolingo = Duolingo(config('USER'), config('PASS'))
    # current_lang = duolingo.get_current_language()
    # explanations = duolingo.get_explanations(current_lang)
    # voices = duolingo.get_voice_url()
    playni = duolingo.get_word_audio_url('你')
    pprint(playni)
    
