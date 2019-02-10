import json
import requests


def getUserData(url):
    i = 0
    char, wordlist, pinyin, explanation = {}, {}, {}, {}
    response = requests.get(url)
    userdata = response.json()
    # Import json for character statistics
    # json_path = os.path.join(settings.BASE_DIR, 'static/json/hanzidb.json')
    json_path = 'DuoTool/duotool.addohm.net/static/json/hanzidb.json'
    with open(json_path, encoding='utf-8') as json_data:
        word_data = json.load(json_data)
        for lang in userdata['language_data']:
            for item in userdata['language_data'][lang]['skills']:
                i += 1
                if item.get('levels_finished') > 0:
                    explanation = {}
                    explanation['index'] = i
                    lessonwords = item.get("words")
                    wordlist[str(lessonwords)] = []
                    explanation['explanation'] = item.get("explanation")
                    wordlist[str(lessonwords)].append(explanation)
                    for word in lessonwords:
                        pinyin = {}
                        pinyin['index'] = i
                        if word in word_data:
                            pinyin['pinyin'] = word_data[word][0]['pinyin']
                        else:
                            pinyin['pinyin'] = ''
                        char[word] = []
                        char[word].append(pinyin)
    word.close()
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
