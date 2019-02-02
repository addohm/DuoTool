import json
import requests


def getUserData(url):
    response = requests.get(url)
    userdata = response.json()
    wordlists, explanations, words = [], [], []

    for language in userdata['language_data']:
        for index in userdata['language_data'][language]['skills']:
            if index.get('levels_finished') > 0:
                wordList = index.get("words")
                wordlists.append(wordList)
                explanations.append(index.get("explanation"))
                for wordItem in wordList:
                    words.append(wordItem)
    return list(zip(wordlists, explanations)), words  # return the value of dictionary from here


def home(request, username='johnny'):
    template_name = 'main/index.html'
    url = "https://www.duolingo.com/users/{}".format(username)
    dictionary, words = getUserData(url)  # catch value of dictionary
    context = {
        'username': username,
        'dictionary': dictionary,
        'words': words,
    }
    print(context)


def main():
    home(None, 'addohm')


if __name__ == "__main__":
    main()
