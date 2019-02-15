import json
import requests
import sys, os



def getUserData(url):
    i = 0
    char, wordlists = {}, {}
    response = requests.get(url)
    userdata = response.json()
    # Import json for character statistics
    # json_path = os.path.join(settings.BASE_DIR, 'static/json/hanzidb.json')
    json_path = os.path.join(os.path.dirname(sys.argv[0]), 'hanzidb.json') # For tests
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
                        pinyin = {}
                        pinyin['index'] = i
                        if word in word_data:
                            pinyin['pinyin'] = word_data[word][0]['pinyin']
                        else:
                            pinyin['pinyin'] = ''
                        char[word] = []
                        char[word].append(pinyin)
    return char, wordlists


def home(request, username='johnny'):
    template_name = 'main/index.html'

    # if request.method == 'POST':
    #     username = request.POST['username']

    url = "https://www.duolingo.com/users/{}".format(username)
    char, wordlists = getUserData(url)  # catch value of dictionary
    context = {
        'username': username,
        'char': char,
        'wordlists': wordlists,
    }
    print(context['username'] + ' contains ' + str(len(context['char'])) + ' chars and ' + str(len(context['wordlists'])) + ' wordlists.')


def main():
    home(None, 'addohm')


if __name__ == "__main__":
    main()
